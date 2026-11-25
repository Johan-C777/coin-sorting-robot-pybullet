"""
Puente Serial <-> Web Local de ULTRA-BAJA LATENCIA para Calibración Robot 4 GDL (ESP32)
---------------------------------------------------------------------------------------
- SIN dependencias externas (Python 3 stdlib + Win32 API).
- Hilo lector en segundo plano que recibe la telemetría push de la ESP32 en tiempo real.
- GET /api/status responde desde memoria RAM en < 0.5 ms (cero tráfico Serial extra!).
- POST /api/move escribe directo a COM5 en < 1 ms sin bloqueos ni PurgeComm.
"""

import ctypes
import ctypes.wintypes as wt
import json
import os
import sys
import threading
import time
import winreg
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "interfaz_calibracion.html")
CONFIG_OUT_PATH = os.path.join(BASE_DIR, "robot_4gdl_calibracion.json")

HOST = "127.0.0.1"
PORT_HTTP = 5050
DEFAULT_BAUD = 115200


def list_com_ports():
    ports = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
        i = 0
        while True:
            try:
                _, val, _ = winreg.EnumValue(key, i)
                ports.append(str(val))
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except OSError:
        pass
    ports.sort(key=lambda s: int(s[3:]) if s.upper().startswith("COM") and s[3:].isdigit() else 999)
    return ports


# ============================================================================
# Driver Serial nativo Windows con hilo lector asíncrono (cero latencia)
# ============================================================================
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
PURGE_RXCLEAR = 0x0008
PURGE_TXCLEAR = 0x0004
MAXDWORD = 0xFFFFFFFF


class DCB(ctypes.Structure):
    _fields_ = [
        ("DCBlength", wt.DWORD),
        ("BaudRate", wt.DWORD),
        ("fFlags", wt.DWORD),
        ("wReserved", wt.WORD),
        ("XonLim", wt.WORD),
        ("XoffLim", wt.WORD),
        ("ByteSize", wt.BYTE),
        ("Parity", wt.BYTE),
        ("StopBits", wt.BYTE),
        ("XonChar", ctypes.c_char),
        ("XoffChar", ctypes.c_char),
        ("ErrorChar", ctypes.c_char),
        ("EofChar", ctypes.c_char),
        ("EvtChar", ctypes.c_char),
        ("wReserved1", wt.WORD),
    ]


class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", wt.DWORD),
        ("ReadTotalTimeoutMultiplier", wt.DWORD),
        ("ReadTotalTimeoutConstant", wt.DWORD),
        ("WriteTotalTimeoutMultiplier", wt.DWORD),
        ("WriteTotalTimeoutConstant", wt.DWORD),
    ]


kernel32 = ctypes.windll.kernel32
kernel32.CreateFileW.restype = wt.HANDLE
kernel32.CreateFileW.argtypes = [
    wt.LPCWSTR, wt.DWORD, wt.DWORD, wt.LPVOID, wt.DWORD, wt.DWORD, wt.HANDLE
]
kernel32.GetCommState.argtypes = [wt.HANDLE, ctypes.POINTER(DCB)]
kernel32.SetCommState.argtypes = [wt.HANDLE, ctypes.POINTER(DCB)]
kernel32.BuildCommDCBW.argtypes = [wt.LPCWSTR, ctypes.POINTER(DCB)]
kernel32.SetCommTimeouts.argtypes = [wt.HANDLE, ctypes.POINTER(COMMTIMEOUTS)]
kernel32.PurgeComm.argtypes = [wt.HANDLE, wt.DWORD]
kernel32.ReadFile.argtypes = [wt.HANDLE, wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
kernel32.WriteFile.argtypes = [wt.HANDLE, wt.LPCVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
kernel32.CloseHandle.argtypes = [wt.HANDLE]


class AsyncWinSerial:
    def __init__(self):
        self.handle = None
        self.port_name = ""
        self.write_lock = threading.Lock()
        self.state_lock = threading.Lock()
        self.running = False
        self.thread = None

        self.latest_status = None
        self.latest_meta = None
        self.last_error = ""
        self.status_event = threading.Event()
        self.meta_event = threading.Event()

    def is_open(self):
        return self.handle is not None and self.running

    def close(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        self.thread = None
        with self.write_lock:
            if self.handle is not None:
                kernel32.CloseHandle(self.handle)
                self.handle = None
                self.port_name = ""

    def open(self, port_name, baud=DEFAULT_BAUD):
        self.close()
        dev_path = f"\\\\.\\{port_name}"
        h = kernel32.CreateFileW(
            dev_path,
            GENERIC_READ | GENERIC_WRITE,
            0,
            None,
            OPEN_EXISTING,
            0,
            None,
        )
        if h == INVALID_HANDLE_VALUE or h is None:
            err = ctypes.get_last_error()
            raise OSError(f"No se pudo abrir {port_name} (Win32 {err}). ¿Está abierto el Monitor Serie?")

        dcb = DCB()
        dcb.DCBlength = ctypes.sizeof(DCB)
        if not kernel32.GetCommState(h, ctypes.byref(dcb)):
            kernel32.CloseHandle(h)
            raise OSError(f"Error leyendo DCB de {port_name}")

        cfg_str = f"baud={baud} parity=N data=8 stop=1 dtr=off rts=off"
        if not kernel32.BuildCommDCBW(cfg_str, ctypes.byref(dcb)):
            kernel32.CloseHandle(h)
            raise OSError(f"Error configurando DCB para {port_name}")

        if not kernel32.SetCommState(h, ctypes.byref(dcb)):
            kernel32.CloseHandle(h)
            raise OSError(f"Error aplicando {baud} baud en {port_name}")

        # Lectura por bloques con retorno inmediato cuando hay datos (máx 15 ms en vacío)
        timeouts = COMMTIMEOUTS()
        timeouts.ReadIntervalTimeout = MAXDWORD
        timeouts.ReadTotalTimeoutMultiplier = MAXDWORD
        timeouts.ReadTotalTimeoutConstant = 15
        timeouts.WriteTotalTimeoutMultiplier = 0
        timeouts.WriteTotalTimeoutConstant = 100
        kernel32.SetCommTimeouts(h, ctypes.byref(timeouts))
        kernel32.PurgeComm(h, PURGE_RXCLEAR | PURGE_TXCLEAR)

        self.handle = h
        self.port_name = port_name
        self.latest_status = None
        self.latest_meta = None
        self.last_error = ""
        self.running = True

        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()

        # Pedir estado inicial y metadatos una sola vez
        self.status_event.clear()
        self.write_line("STATUS")
        if not self.status_event.wait(timeout=1.5):
            # Reintento por si la ESP32 estaba terminando de arrancar
            self.write_line("STATUS")
            if not self.status_event.wait(timeout=1.5):
                self.close()
                raise TimeoutError(f"{port_name} no respondió STATUS de la ESP32")

    def _reader_loop(self):
        buf = bytearray()
        chunk = ctypes.create_string_buffer(512)
        read_n = wt.DWORD(0)

        while self.running and self.handle is not None:
            ok = kernel32.ReadFile(self.handle, chunk, 512, ctypes.byref(read_n), None)
            if not ok:
                time.sleep(0.02)
                continue
            n = read_n.value
            if n <= 0:
                continue
            buf.extend(chunk.raw[:n])
            while True:
                idx = buf.find(b"\n")
                if idx < 0:
                    break
                raw_line = bytes(buf[:idx]).decode("utf-8", errors="replace").strip()
                del buf[:idx + 1]
                if not raw_line.startswith("{"):
                    continue
                try:
                    msg = json.loads(raw_line)
                except Exception:
                    continue
                mtype = msg.get("type", "")
                with self.state_lock:
                    if mtype == "status" or "motors" in msg:
                        msg["connected"] = True
                        msg["port"] = self.port_name
                        self.latest_status = msg
                        self.status_event.set()
                    elif mtype == "meta" or "uiMeta" in msg:
                        self.latest_meta = msg
                        self.meta_event.set()
                    elif mtype == "err" or "error" in msg:
                        self.last_error = msg.get("error", "")

    def write_line(self, cmd):
        with self.write_lock:
            if self.handle is None:
                raise OSError("Puerto serial no conectado")
            data = (cmd.strip() + "\n").encode("utf-8")
            written = wt.DWORD(0)
            ok = kernel32.WriteFile(self.handle, data, len(data), ctypes.byref(written), None)
            if not ok or written.value != len(data):
                raise OSError("Error escribiendo en puerto serial")

    def get_cached_status(self):
        with self.state_lock:
            return dict(self.latest_status) if self.latest_status else None

    def request_meta(self):
        self.meta_event.clear()
        self.write_line("GET_META")
        if self.meta_event.wait(timeout=1.2):
            with self.state_lock:
                return dict(self.latest_meta) if self.latest_meta else {"ok": True, "uiMeta": {}}
        return {"ok": True, "uiMeta": {}}


esp_serial = AsyncWinSerial()


class CalibrationHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if args and "/api/status" in str(args[0]):
            return
        sys.stdout.write(f"[HTTP] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except OSError:
            pass

    def _send_html(self):
        with open(HTML_PATH, "rb") as f:
            body = f.read()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except OSError:
            pass

    def _read_body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        return self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_html()
            return

        if parsed.path == "/api/ports":
            self._send_json(200, {
                "ports": list_com_ports(),
                "connectedPort": esp_serial.port_name if esp_serial.is_open() else ""
            })
            return

        if parsed.path == "/api/meta":
            if not esp_serial.is_open():
                self._send_json(503, {"error": "Sin puerto serial conectado"})
                return
            try:
                self._send_json(200, esp_serial.request_meta())
            except Exception as e:
                self._send_json(503, {"error": str(e)})
            return

        if parsed.path == "/api/status":
            if not esp_serial.is_open():
                self._send_json(503, {"error": "Sin puerto serial conectado"})
                return
            st = esp_serial.get_cached_status()
            if st is None:
                self._send_json(503, {"error": "Esperando estado inicial de ESP32"})
                return
            self._send_json(200, st)
            return

        self._send_json(404, {"error": "Ruta no encontrada"})

    def do_POST(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        arg = lambda k, d="": qs.get(k, [d])[0]

        if parsed.path == "/api/connect":
            port = arg("port")
            if not port:
                self._send_json(400, {"error": "Falta parametro port"})
                return
            try:
                esp_serial.open(port, DEFAULT_BAUD)
                self._send_json(200, {"ok": True, "port": port})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        if parsed.path == "/api/save_config_file":
            body = self._read_body()
            try:
                parsed_json = json.loads(body)
                with open(CONFIG_OUT_PATH, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                self._send_json(200, {"ok": True, "path": CONFIG_OUT_PATH})
            except Exception as e:
                self._send_json(400, {"error": f"No se pudo guardar JSON: {e}"})
            return

        if not esp_serial.is_open():
            self._send_json(503, {"error": "Puerto serial no conectado"})
            return

        # Escritura directa sin esperas bloqueantes (< 1 ms!)
        cmd = None
        wait_status = False
        if parsed.path == "/api/move":
            cmd = f"MOVE {arg('motor')} {arg('steps')}"
        elif parsed.path == "/api/goto":
            cmd = f"GOTO {arg('motor')} {arg('pos')}"
        elif parsed.path == "/api/home_all":
            cmd = "HOME_ALL"
            wait_status = True
        elif parsed.path == "/api/zero":
            cmd = f"ZERO {arg('motor')}"
            wait_status = True
        elif parsed.path == "/api/set_limit":
            cmd = f"LIMIT {arg('motor')} {arg('side').upper()}"
            wait_status = True
        elif parsed.path == "/api/clear_limits":
            cmd = f"CLEAR_LIMITS {arg('motor')}"
            wait_status = True
        elif parsed.path == "/api/invert":
            cmd = f"INVERT {arg('motor')} {arg('val')}"
            wait_status = True
        elif parsed.path == "/api/speed":
            cmd = f"SPEED {arg('val')}"
            wait_status = True
        elif parsed.path == "/api/enable":
            cmd = f"ENABLE {arg('val')}"
            wait_status = True
        elif parsed.path == "/api/stop":
            cmd = "STOP"
            wait_status = True
        elif parsed.path == "/api/servos/center":
            cmd = "SERVOS_CENTER"
            wait_status = True
        elif parsed.path == "/api/save_nvs":
            body = self._read_body().replace("\r", "").replace("\n", "")
            cmd = f"SAVE_NVS {body}"
            wait_status = True

        if cmd is None:
            self._send_json(404, {"error": "Endpoint no encontrado"})
            return

        try:
            if wait_status:
                esp_serial.status_event.clear()
            esp_serial.write_line(cmd)
            if wait_status:
                esp_serial.status_event.wait(timeout=0.35)
            self._send_json(200, {"ok": True})
        except Exception as e:
            self._send_json(503, {"error": str(e)})


def auto_connect(preferred=None):
    ports = list_com_ports()
    candidates = []
    if preferred and preferred in ports:
        candidates.append(preferred)
    for p in ports:
        if p not in candidates:
            candidates.append(p)
    for p in candidates:
        try:
            esp_serial.open(p, DEFAULT_BAUD)
            print(f"[SERIAL] Conectado (baja latencia) a ESP32 en {p} ({DEFAULT_BAUD} baud)", flush=True)
            return p
        except Exception as e:
            print(f"[SERIAL] {p} no respondió como ESP32: {e}", flush=True)
            esp_serial.close()
    print("[SERIAL] No se conectó automáticamente. Selecciona el puerto COM desde la web.", flush=True)
    return None


if __name__ == "__main__":
    pref = sys.argv[1] if len(sys.argv) > 1 else "COM5"
    auto_connect(pref)
    httpd = None
    bound_port = PORT_HTTP
    for candidate in (PORT_HTTP, 5051, 8765, 8888, 18080):
        try:
            httpd = ThreadingHTTPServer((HOST, candidate), CalibrationHandler)
            bound_port = candidate
            break
        except OSError:
            continue
    if httpd is None:
        httpd = ThreadingHTTPServer((HOST, 0), CalibrationHandler)
        bound_port = httpd.server_address[1]
    print(f"[WEB] Interfaz lista en: http://{HOST}:{bound_port}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        esp_serial.close()
        httpd.server_close()
