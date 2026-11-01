// =============================================================================================
//  Módulo clasificador de monedas colombianas · Etapa 1 · ESP32-S3
//  Sistema de Logística de Monedas Inteligentes — Micros y Laboratorio, UMNG
//
//  Tolva de disco (28BYJ-48) -> pista de canto a 22° con 2 barreras IR (diámetro por tiempo
//  de vuelo, ISR) -> TCS3200 (PCNT) para $500 antigua/nueva -> embudo -> compuerta SG90
//  -> vaso del cartucho que la banda pone debajo.
//
//  Capas:  lib/Clasificacion  medición y decisión (portable, probada en el PC)
//          lib/Secuenciador   máquina de estados del ciclo (portable, probada en el PC)
//          src/hal            hardware del ESP32-S3: ISR, PCNT, timer, servo, pasos
//          src/main.cpp       arranque, consola serie, persistencia y estado
// =============================================================================================
#include <Arduino.h>
#include <Preferences.h>

#include "Calibrador.h"
#include "Secuenciador.h"
#include "calibracion.h"
#include "config.h"
#include "hal/Actuadores.h"
#include "hal/Barreras.h"
#include "hal/Boton.h"
#include "hal/Color.h"
#include "hal/PlantaESP32.h"
#include "pines.h"

using monedas::TIPOS;

static hal::Color color;
static hal::PlantaESP32 planta(color);
static seq::Secuenciador ciclo(planta, CAL_FABRICA, TEMPORIZACION);
static hal::Boton boton;
static clasif::Calibrador calibrador;
static int8_t vaso_calibrando = -2;            // -2 = fuera del modo calibración
static bool monitor = false;
static uint32_t t_monitor = 0;

// ---- Persistencia de la calibración en NVS ---------------------------------------------------
namespace nvs {
constexpr uint16_t VERSION = 1;                // cambiar si cambia clasif::Calibracion
Preferences pref;

bool cargar(clasif::Calibracion &c) {
  pref.begin("clasif", true);
  const bool ok = pref.getUShort("ver", 0) == VERSION && pref.getBytesLength("cal") == sizeof(c);
  if (ok) pref.getBytes("cal", &c, sizeof(c));
  pref.end();
  return ok;
}
void guardar(const clasif::Calibracion &c) {
  pref.begin("clasif", false);
  pref.putUShort("ver", VERSION);
  pref.putBytes("cal", &c, sizeof(c));
  pref.end();
}
void borrar() {
  pref.begin("clasif", false);
  pref.clear();
  pref.end();
}
}  // namespace nvs

// ---- Salida: una línea por moneda (protocolo de docs/04-protocolo.md) ------------------------
static void alResultado(const seq::Resultado &r, void *) {
  const clasif::Medicion &m = r.medicion;
  Serial.printf("#D n=%lu v0=%.0f a=%.0f c=%.2f D=%.2f razon=%.2f -> %s (%s)\n", (unsigned long)r.numero,
                m.v0_mm_s, m.a_mm_s2, m.cuerda_mm, m.diametro_mm, r.razon_color,
                r.vaso >= 0 ? TIPOS[r.vaso].codigo : "RECHAZO", clasif::texto(r.motivo));
  if (r.vaso >= 0)
    Serial.printf("M:%u,%d,%s\n", TIPOS[r.vaso].valor, r.vaso,
                  TIPOS[r.vaso].familia == monedas::Familia::Antigua ? "antigua" : "nueva");
  else
    Serial.printf("R:%s,%.2f\n", clasif::texto(r.motivo), m.diametro_mm);

  // Modo calibración: cada medición válida es una muestra de la moneda conocida.
  if (vaso_calibrando >= 0 && m.motivo == clasif::Motivo::Ok) {
    const float c_bruta = m.cuerda_mm + ciclo.calibracion().ancho_haz_mm;
    calibrador.agregar(c_bruta, TIPOS[vaso_calibrando].diametro_mm);
    Serial.printf("CAL muestra %u: %s c=%.3f (%u tipos)\n", calibrador.muestras(), TIPOS[vaso_calibrando].codigo,
                  c_bruta, calibrador.tiposDistintos());
  }
}

// Trama del lote para el brazo: VASOS:50x30a6,100x24a4,...  (aN = antiguas)
static void tramaVasos() {
  const uint16_t den[5] = {50, 100, 200, 500, 1000};
  Serial.print("VASOS:");
  bool primero = true;
  for (uint16_t d : den) {
    uint16_t n = 0, a = 0;
    for (uint8_t v = 0; v < monedas::N_VASOS; v++)
      if (TIPOS[v].valor == d) {
        n += ciclo.cuenta(v);
        if (TIPOS[v].familia == monedas::Familia::Antigua) a += ciclo.cuenta(v);
      }
    if (!n) continue;
    Serial.printf(primero ? "%ux%u" : ",%ux%u", d, n);
    if (a) Serial.printf("a%u", a);
    primero = false;
  }
  Serial.println();
}

static void info() {
  const clasif::Calibracion &c = ciclo.calibracion();
  Serial.printf("Clasificador etapa 1 v%s | estado %s | falla: %s | auto %s\n", FW_VERSION,
                seq::texto(ciclo.estado()), seq::texto(ciclo.falla()), ciclo.automatico() ? "ON" : "OFF");
  Serial.printf("CAL sep=%.2f h=%.3f ancho=%.3f tol=%.2f margen=%.2f dorado=%.2f | barreras %s\n",
                c.sep_barreras_mm, c.h_haz_mm, c.ancho_haz_mm, c.tolerancia_max_mm, c.margen_vecino_mm,
                c.umbral_dorado, BARRERAS_MODO == BARRERAS_DIGITAL ? "digital (ISR por flanco)" : "ADC (timer ISR)");
  for (uint8_t v = 0; v < monedas::N_VASOS; v++)
    Serial.printf("  vaso %u %-6s D=%.2f tol=%.2f  n=%u\n", v, TIPOS[v].codigo, TIPOS[v].diametro_mm,
                  clasif::tolerancia(v, c), ciclo.cuenta(v));
  Serial.printf("  rechazo n=%u | total %lu | eventos perdidos %lu\n", ciclo.rechazos(),
                (unsigned long)ciclo.total(), (unsigned long)hal::barrerasPerdidos());
}

static void ayuda() {
  Serial.println(F(
      "a auto on/off | d un ciclo | e PARO | R rearmar | i estado | r resumen + trama VASOS\n"
      "f/b bolsillo adelante/atras | o/p abrir/cerrar compuerta | w<grados> servo\n"
      "v<pps> k<pps2> s<pps> tolva (vmax, acel, v0) | t barrido de velocidad de la tolva\n"
      "m monitor de sensores | x<vaso> vaciar vaso (-1 todos) | z<vaso> banda a vaso\n"
      "CALIBRACION: c<vaso> pasar monedas de ese tipo | c-1 salir | C ajustar haz | u<umbral> dorado\n"
      "             g guardar en flash | l cargar | F valores de fabrica"));
}

static void barrido() {          // [CAL-09] 1 vuelta por velocidad: ¿dónde empieza a perder pasos?
  Rampa &t = hal::tolva();
  const float v_ant = t.vmax;
  for (float v = 400; v <= 1400; v += 100) {
    t.vmax = v;
    Serial.printf("vmax=%.0f pps (%.1f rpm)\n", v, v * 60 / TOLVA_PASOS_VUELTA);
    hal::tolvaBolsillos(BOLSILLOS);
    while (hal::tolvaOcupada()) delay(2);
    delay(500);
  }
  t.vmax = v_ant;
  Serial.println(F("Usa ~75 % de la ultima velocidad en que no perdio pasos (TOLVA_VMAX)."));
}

static void consola() {
  static char buf[24];
  static uint8_t n = 0;
  while (Serial.available()) {
    const char ch = Serial.read();
    if (ch != '\n' && ch != '\r') { if (n < sizeof(buf) - 1) buf[n++] = ch; continue; }
    if (!n) continue;
    buf[n] = 0;
    n = 0;
    const float x = atof(buf + 1);
    const bool con_numero = buf[1] != 0;
    clasif::Calibracion cal = ciclo.calibracion();
    switch (buf[0]) {
      case 'a': ciclo.automatico() ? ciclo.pausa() : ciclo.marcha(); Serial.println(ciclo.automatico() ? "auto ON" : "auto OFF"); break;
      case 'd': ciclo.unCiclo(); break;
      case 'e': ciclo.paro(); Serial.println(F("PARO")); break;
      case 'R': ciclo.reset(); info(); break;
      case 'i': info(); break;
      case 'r': info(); tramaVasos(); break;
      case 'f': hal::tolvaBolsillos(1); break;
      case 'b': hal::tolvaBolsillos(-1); break;
      case 'o': hal::compuerta(true); break;
      case 'p': hal::compuerta(false); break;
      case 'w': hal::compuertaAngulo((int)x); break;
      case 'v': hal::tolva().vmax = constrain(x, 100, 1600); Serial.printf("vmax=%.0f\n", hal::tolva().vmax); break;
      case 'k': hal::tolva().acc = constrain(x, 200, 20000); Serial.printf("acc=%.0f\n", hal::tolva().acc); break;
      case 's': hal::tolva().v0 = constrain(x, 50, 400); Serial.printf("v0=%.0f\n", hal::tolva().v0); break;
      case 't': barrido(); break;
      case 'm': monitor = !monitor; break;
      case 'x': ciclo.vaciarVaso(con_numero ? (int8_t)x : -1); break;
      case 'z': hal::bandaVaso((int8_t)x); break;
      case 'c':
        vaso_calibrando = (con_numero && x >= 0 && x < monedas::N_VASOS) ? (int8_t)x : -2;
        if (vaso_calibrando >= 0) Serial.printf("CAL: pasa monedas %s; 'C' para ajustar\n", TIPOS[vaso_calibrando].codigo);
        else Serial.println(F("CAL: modo calibracion apagado"));
        break;
      case 'C': {
        const clasif::Calibrador::Ajuste a = calibrador.ajustar();
        if (!a.valido) { Serial.println(F("CAL: hacen falta >= 6 muestras de >= 2 tipos")); break; }
        clasif::Calibrador::aplicar(a, cal);
        ciclo.calibracion(cal);
        Serial.printf("CAL: h=%.3f ancho=%.3f | error RMS %.3f mm, max %.3f mm. 'g' para guardar\n", a.h_mm,
                      a.ancho_mm, a.rms_diametro_mm, a.max_diametro_mm);
        calibrador.reiniciar();
        break;
      }
      case 'u': cal.umbral_dorado = x; ciclo.calibracion(cal); Serial.printf("umbral dorado=%.2f\n", x); break;
      case 'g': nvs::guardar(ciclo.calibracion()); Serial.println(F("calibracion guardada en flash")); break;
      case 'l': if (nvs::cargar(cal)) ciclo.calibracion(cal); info(); break;
      case 'F': nvs::borrar(); ciclo.calibracion(CAL_FABRICA); info(); break;
      default: ayuda();
    }
  }
}

static void imprimirMonitor() {
  const hal::DiagBarrera b1 = hal::barrerasDiag(0), b2 = hal::barrerasDiag(1);
  uint32_t r, g, b;
  const seq::LecturaColor c = color.leer();
  color.crudo(r, g, b);
  Serial.printf("IR1=%d/%.0f%s IR2=%d/%.0f%s | TCS R=%lu G=%lu B=%lu razon=%.2f | %s\n", b1.crudo, b1.base,
                b1.ocupada ? "*" : " ", b2.crudo, b2.base, b2.ocupada ? "*" : " ", (unsigned long)r,
                (unsigned long)g, (unsigned long)b, c.razon, seq::texto(ciclo.estado()));
}

// LED RGB de la placa como indicador de estado (si la variante lo define).
static void ledEstado() {
#ifdef RGB_BUILTIN
  static seq::Estado previo = seq::Estado::Falla;
  static bool primero = true;
  const seq::Estado e = ciclo.estado();
  if (!primero && e == previo) return;
  primero = false;
  previo = e;
  uint8_t r = 0, g = 0, b = 0;
  switch (e) {
    case seq::Estado::Reposo: g = 8; break;
    case seq::Estado::Falla: r = 32; break;
    case seq::Estado::TolvaVacia: r = 16; g = 8; break;
    case seq::Estado::Midiendo:
    case seq::Estado::LeyendoColor: b = 24; break;
    default: g = 16; b = 8;
  }
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  rgbLedWrite(RGB_BUILTIN, r, g, b);
#else
  neopixelWrite(RGB_BUILTIN, r, g, b);
#endif
#endif
}

void setup() {
  Serial.begin(115200);
  delay(300);
  clasif::Calibracion cal = CAL_FABRICA;
  const bool de_flash = nvs::cargar(cal);
  ciclo.calibracion(cal);
  ciclo.alResultado(alResultado, nullptr);

  hal::actuadoresIniciar();
  color.iniciar();
  hal::barrerasIniciar();        // toma la base con la pista vacía
  boton.iniciar();
  enableLoopWDT();               // si loop() se cuelga > 5 s, el ESP32 se reinicia

  Serial.printf("\nClasificador de monedas · etapa 1 · v%s · calibracion de %s\n", FW_VERSION,
                de_flash ? "flash" : "fabrica");
  info();
  ayuda();
}

void loop() {
  ciclo.actualizar(millis());
  consola();
  switch (boton.pulsacion()) {
    case hal::Pulsacion::Corta: ciclo.automatico() ? ciclo.pausa() : ciclo.marcha(); break;
    case hal::Pulsacion::Larga: ciclo.paro(); Serial.println(F("PARO (boton)")); break;
    default: break;
  }
  if (monitor && millis() - t_monitor > 200) {
    t_monitor = millis();
    imprimirMonitor();
  }
  ledEstado();
}
