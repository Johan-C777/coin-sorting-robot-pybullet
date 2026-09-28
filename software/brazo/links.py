"""Enlaces de salida hacia el robot: serie, HTTP o simulado.

Todos exponen el mismo método enviar(trama). Así el controlador no sabe si
detrás hay un ESP32 real, una simulación o solo un registro en consola.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from typing import List, Optional


class EnlaceNulo:
    """Guarda las tramas en memoria. Útil para pruebas y para la simulación."""

    def __init__(self, eco: bool = False):
        self.tramas: List[str] = []
        self.eco = eco

    def enviar(self, trama: str) -> None:
        self.tramas.append(trama)
        if self.eco:
            print(trama, file=sys.stdout)

    def cerrar(self) -> None:
        pass


class EnlaceSerie:
    """Puerto serie a 115200 baudios contra firmware/esp32_brazo."""

    def __init__(self, puerto: str = "/dev/ttyUSB0", baudios: int = 115200,
                 espera_inicio: float = 2.0):
        import serial  # pyserial, se importa aquí para no exigirlo siempre
        self.ser = serial.Serial(puerto, baudios, timeout=0.2)
        time.sleep(espera_inicio)   # el ESP32 se reinicia al abrir el puerto

    def enviar(self, trama: str) -> Optional[str]:
        self.ser.write((trama + "\n").encode("ascii"))
        return self.ser.readline().decode("ascii", "ignore").strip() or None

    def cerrar(self) -> None:
        self.ser.close()


class EnlaceHTTP:
    """Servidor web del ESP32 en la red Wi-Fi local."""

    def __init__(self, host: str = "192.168.1.50", timeout: float = 2.0):
        self.base = f"http://{host}"
        self.timeout = timeout

    def _post(self, ruta: str, cuerpo: dict) -> dict:
        datos = json.dumps(cuerpo).encode("utf-8")
        req = urllib.request.Request(self.base + ruta, data=datos,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8") or "{}")

    def enviar(self, trama: str) -> dict:
        return self._post("/api/pose", {"trama": trama})

    def ordenar(self, criterio: str, sentido: str) -> dict:
        return self._post("/api/ordenar", {"criterio": criterio, "sentido": sentido})

    def vasos(self, lista: List[dict]) -> dict:
        return self._post("/api/vasos", {"entrada": lista})

    def estado(self) -> dict:
        with urllib.request.urlopen(self.base + "/api/estado", timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def cerrar(self) -> None:
        pass
