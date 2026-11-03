// Etapa 1 completa en ESP32-S3: tolva 28BYJ-48 -> barreras IR (diámetro) -> TCS3200
// ($500 A/N) -> compuerta SG90 -> (opcional) banda NEMA17/A4988.
// Consola serie 115200: ver ayuda() abajo.
#include <Arduino.h>
#include <esp_rom_sys.h>
#include "config.h"
#include "actuadores.h"
#include "sensores.h"

Barrera b1(PIN_IR1), b2(PIN_IR2);
Color color;

enum Estado { REPOSO, AVANZA, ESPERA, MIDE, POSICIONA, ABRE, CIERRA } est = REPOSO;
bool automatico = AUTO_AL_ARRANCAR, monitor = false;
uint32_t t_est = 0, t_mon = 0;
uint8_t vacios = 0;
bool giro = false;                                // giro continuo de la tolva (sin sensores)
uint16_t espera_ms = ESPERA_MONEDA_MS;           // 'e<ms>' lo cambia en caliente
int vaso = VASO_RECHAZO;
uint16_t cuenta[10] = {};                         // 0..8 vasos, 9 rechazo

void ayuda() {
  Serial.println(F("g=giro continuo del motor  a=auto on/off  d=1 ciclo  f/b=1 bolsillo  o/p=abrir/cerrar compuerta\n"
                   "v<pps>=vmax  k<pps2>=acel  s<pps>=v0 (tolva)  e<ms>=espera por bolsillo  t=barrido\n"
                   "m=monitor sensores  r=resumen  x<mm>/z<vaso>=banda (HABILITAR_BANDA)"));
}

void cambiar(Estado e) { est = e; t_est = millis(); }

// Una moneda: tiempos de las dos barreras -> velocidad -> cuerda -> tipo.
void medirYClasificar() {
  const float dt12 = (b2.t_ent - b1.t_ent) * 1e-6f;               // s entre barreras
  const float v = SEP_BARRERAS_MM / dt12;                          // mm/s
  const float c1 = v * (b1.t_sal - b1.t_ent) * 1e-6f;
  const float c2 = v * (b2.t_sal - b2.t_ent) * 1e-6f;
  const float cuerda = (c1 + c2) / 2;                              // c2 es la más fiable (ya acelerada)
  int mejor = -1;
  float dm = 1e9f;
  for (int i = 0; i < 9; i++) {
    if (i == V_500N) continue;                                     // $500 A/N: mismo tamaño, decide el color
    const float d = fabsf(cuerda - TIPOS[i].cuerda_mm * K_CUERDA);
    if (d < dm) { dm = d; mejor = i; }
  }
  float razon = 0;
  if (dm <= TOLERANCIA_MM && mejor == V_500A) {
    razon = color.razonMax(150);                                   // moneda frente a la ventana del TCS
    mejor = razon > UMBRAL_DORADO ? V_500N : V_500A;
  }
  vaso = dm <= TOLERANCIA_MM ? mejor : VASO_RECHAZO;
  Serial.printf("MONEDA v=%.0f mm/s c1=%.2f c2=%.2f razon=%.2f -> %s\n", v, c1, c2, razon,
                vaso >= 0 ? TIPOS[vaso].nombre : "RECHAZO");
  cuenta[vaso >= 0 ? vaso : 9]++;
}

void ciclo() {
  switch (est) {
    case REPOSO:
      if (automatico && millis() - t_est > 150) {
        b1.borrar(); b2.borrar();
        tolvaBolsillos(1);
        cambiar(AVANZA);
      }
      break;
    case AVANZA:                                   // la moneda cae mientras el bolsillo pasa
    case ESPERA:
      if (b1.nueva_ent) { vacios = 0; cambiar(MIDE); break; }
      if (est == AVANZA && !tolva.ocupado()) cambiar(ESPERA);
      else if (est == ESPERA && millis() - t_est > espera_ms) {
        Serial.println(F("bolsillo vacio"));
        if (++vacios >= VACIOS_PARA_PARAR) {
          vacios = 0;
#if PARAR_SI_VACIA
          automatico = false;
          Serial.println(F("TOLVA VACIA: auto apagado"));
#else
          Serial.println(F("una vuelta sin monedas (sigue girando; 'a' para parar)"));
#endif
        }
        cambiar(REPOSO);
      }
      break;
    case MIDE:
      if (b1.nueva_sal && b2.nueva_sal) {
        medirYClasificar();
#if HABILITAR_BANDA
        bandaA(vaso >= 0 ? bandaPosVaso(vaso) : BANDA_RECHAZO_MM);
#endif
        cambiar(POSICIONA);
      } else if (millis() - t_est > 1500) {
        Serial.println(F("ERROR medicion (atasco o barrera 2 sin cortar)"));
        cambiar(REPOSO);
      }
      break;
    case POSICIONA:
      if (millis() - t_est > LLEGADA_MONEDA_MS
#if HABILITAR_BANDA
          && !banda.ocupado()
#endif
      ) { servoGrados(SERVO_ABIERTA); cambiar(ABRE); }
      break;
    case ABRE:
      if (millis() - t_est > COMPUERTA_ABIERTA_MS) { servoGrados(SERVO_CERRADA); cambiar(CIERRA); }
      break;
    case CIERRA:
      if (millis() - t_est > 250) cambiar(REPOSO);
      break;
  }
}

void barrido() {                                  // 1 vuelta por velocidad: ¿dónde empieza a fallar?
  const float v_ant = tolva.vmax;
  for (float v = 400; v <= 1400; v += 100) {
    tolva.vmax = v;
    Serial.printf("vmax=%.0f pps (%.1f rpm)\n", v, v * 60 / TOLVA_PASOS_VUELTA);
    tolvaBolsillos(BOLSILLOS);
    while (tolva.ocupado()) delay(2);
    delay(500);
  }
  tolva.vmax = v_ant;
  Serial.println(F("Usa ~75 % de la ultima velocidad en que no perdio pasos."));
}

void consola() {
  static char buf[24];
  static uint8_t n = 0;
  static uint32_t t_car = 0;
  // Ejecuta con Enter o, si no hay Enter, 60 ms después del último carácter.
  bool listo = n && millis() - t_car > 60;
  while (Serial.available() && !listo) {
    const char ch = Serial.read();
    t_car = millis();
    if (ch != '\n' && ch != '\r') { if (n < sizeof(buf) - 1) buf[n++] = ch; continue; }
    listo = true;
  }
  if (listo) {
    if (!n) return;
    buf[n] = 0; n = 0;
    const float x = atof(buf + 1);
    switch (buf[0]) {
      case 'g': giro = !giro; if (giro) { automatico = false; tolva.mover(100000000L * TOLVA_SENTIDO); } else tolva.parar();
                Serial.println(giro ? "giro continuo ON ('g' para parar, v<pps> cambia la velocidad)" : "giro OFF"); break;
      case 'a': if (giro) { giro = false; tolva.parar(); }
                automatico = !automatico; vacios = 0; Serial.println(automatico ? "auto ON" : "auto OFF"); break;
      case 'd': b1.borrar(); b2.borrar(); tolvaBolsillos(1); cambiar(AVANZA); break;
      case 'f': tolvaBolsillos(1); Serial.println("+1 bolsillo"); break;
      case 'b': tolvaBolsillos(-1); Serial.println("-1 bolsillo"); break;
      case 'o': servoGrados(SERVO_ABIERTA); break;
      case 'p': servoGrados(SERVO_CERRADA); break;
      case 'v': tolva.vmax = constrain(x, 100, 1600); Serial.printf("vmax=%.0f\n", tolva.vmax); break;
      case 'k': tolva.acc = constrain(x, 200, 20000); Serial.printf("acc=%.0f\n", tolva.acc); break;
      case 's': tolva.v0 = constrain(x, 50, 400); Serial.printf("v0=%.0f\n", tolva.v0); break;
      case 'e': espera_ms = constrain((int)x, 150, 5000); Serial.printf("espera=%u ms\n", espera_ms); break;
      case 't': barrido(); break;
      case 'm': monitor = !monitor; break;
      case 'r':
        for (int i = 0; i < 9; i++) Serial.printf("%s=%u ", TIPOS[i].nombre, cuenta[i]);
        Serial.printf("RECHAZO=%u\n", cuenta[9]);
        break;
#if HABILITAR_BANDA
      case 'x': bandaA(x); break;
      case 'z': bandaA(bandaPosVaso(constrain((int)x, 0, 8))); break;
#endif
      default: ayuda();
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println(F("\n== Etapa 1 arrancando =="));
  Serial.flush();
  tolvaIniciar();       Serial.println(F("tolva ok"));
  compuertaIniciar();   Serial.println(F("servo ok"));
#if HABILITAR_BANDA
  bandaIniciar();
#endif
  b1.iniciar(); b2.iniciar();
  Serial.printf("IR base: B1=%.0f B2=%.0f\n", b1.base, b2.base);
  color.iniciar();      Serial.println(F("tcs ok"));
  iniciarTareaPasos();  Serial.println(F("tarea pasos ok"));
  ayuda();
  if (automatico) Serial.println(F("AUTO ON: ciclo continuo ('a' alterna)"));
#if GIRO_AL_ARRANCAR
  giro = true; tolva.mover(100000000L * TOLVA_SENTIDO);
  Serial.println(F("GIRO CONTINUO ON: solo motor, sin sensores ('g' para/arranca, 'a' = ciclo completo)"));
#endif
}

void loop() {
  b1.leer();
  b2.leer();
  ciclo();
  consola();
  if (monitor && millis() - t_mon > 200) {
    t_mon = millis();
    uint32_t tot;
    const float rz = color.razonMax(10, &tot);
    Serial.printf("IR1=%d/%.0f IR2=%d/%.0f REF=%d  TCS razon=%.2f total=%u\n", b1.raw, b1.base, b2.raw,
                  b2.base, analogRead(PIN_IR_REF), rz, tot);
  }
  // Fuera de la medición se duerme 1 ms para que IDLE1 alimente el watchdog.
  if (est != AVANZA && est != ESPERA && est != MIDE) delay(1);
}
