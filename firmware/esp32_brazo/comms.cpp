#include "comms.h"

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

#include <stdlib.h>
#include <string.h>

#include "protocol.h"

namespace {
WebServer servidor(80);
Comms *instancia = nullptr;

int8_t zonaDeTexto(const char *t) { return (t[0] == 'r' || t[0] == 'R') ? ZONA_RACK : ZONA_ENTRADA; }

uint8_t criterioDeTexto(const char *t) {
  if (strncmp(t, "den", 3) == 0) return POR_DENOMINACION;
  if (strncmp(t, "can", 3) == 0) return POR_CANTIDAD;
  if (strncmp(t, "pes", 3) == 0) return POR_PESO;
  return POR_VALOR;
}
}  // namespace

void Comms::iniciarSerie(unsigned long baudios) {
  Serial.begin(baudios);
  instancia = this;
  Serial.println(F("brazo clasificador listo"));
}

bool Comms::iniciarWifi(const char *ssid, const char *clave, uint16_t segundos) {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, clave);
  const uint32_t limite = millis() + (uint32_t)segundos * 1000UL;
  while (WiFi.status() != WL_CONNECTED && millis() < limite) delay(250);
  wifi_ = (WiFi.status() == WL_CONNECTED);
  if (wifi_) {
    Serial.print(F("wifi listo en "));
    Serial.println(WiFi.localIP());
    rutasHttp();
    servidor.begin();
  } else {
    Serial.println(F("sin wifi: se sigue por puerto serie"));
  }
  return wifi_;
}

void Comms::estadoJson(char *destino, size_t capacidad) const {
  const float *q = bus_.pose();
  char trama[32];
  bus_.trama(trama, sizeof(trama));
  int n = snprintf(destino, capacidad,
      "{\"estado\":\"%s\",\"paso\":%u,\"total\":%u,\"mensaje\":\"%s\","
      "\"q\":[%.2f,%.2f,%.2f,%.2f,%.2f],\"pinza_mm\":%.1f,\"trama\":\"%s\",\"vasos\":[",
      sec_.ocupado() ? "moviendo" : "listo", sec_.paso(), sec_.total(), sec_.mensaje(),
      q[0], q[1], q[2], q[3], q[4], bus_.pinza(), trama);
  for (uint8_t i = 0; i < N_PUESTOS && n > 0 && (size_t)n < capacidad; i++) {
    n += snprintf(destino + n, capacidad - n,
        "%s{\"zona\":\"%s\",\"puesto\":%d,\"den\":%u,\"n\":%u,\"valor\":%lu,\"peso_g\":%.1f}",
        i ? "," : "", vasos_[i].zona == ZONA_RACK ? "rack" : "entrada",
        vasos_[i].puesto + 1, vasos_[i].denominacion, vasos_[i].monedas,
        (unsigned long)Vasos::valor(vasos_[i]), Vasos::pesoG(vasos_[i]));
  }
  snprintf(destino + n, capacidad - n, "]}");
}

void Comms::rutasHttp() {
  servidor.on("/api/estado", HTTP_GET, []() {
    char json[768];
    instancia->estadoJson(json, sizeof(json));
    servidor.send(200, "application/json", json);
  });

  servidor.on("/api/ordenar", HTTP_POST, []() {
    const String cuerpo = servidor.arg("plain");
    const uint8_t criterio = criterioDeTexto(cuerpo.indexOf("peso") > 0 ? "pes" :
                              cuerpo.indexOf("cantidad") > 0 ? "can" :
                              cuerpo.indexOf("denominacion") > 0 ? "den" : "val");
    const int8_t sentido = (cuerpo.indexOf("desc") > 0) ? -1 : 1;
    const bool ok = instancia->sec_.iniciar(instancia->vasos_, criterio, sentido);
    servidor.send(ok ? 200 : 409, "application/json",
                  ok ? "{\"ok\":true}" : "{\"ok\":false}");
  });

  servidor.on("/api/vasos", HTTP_POST, []() {
    // Formato esperado: {"entrada":[{"den":500,"n":12}, ...]} en orden de puesto.
    String cuerpo = servidor.arg("plain");
    int desde = 0;
    for (uint8_t i = 0; i < N_PUESTOS; i++) {
      const int posDen = cuerpo.indexOf("\"den\"", desde);
      const int posN = cuerpo.indexOf("\"n\"", posDen);
      if (posDen < 0 || posN < 0) break;
      instancia->vasos_[i].denominacion = (uint16_t)cuerpo.substring(posDen + 6).toInt();
      instancia->vasos_[i].monedas = (uint8_t)cuerpo.substring(posN + 4).toInt();
      instancia->vasos_[i].zona = ZONA_ENTRADA;
      instancia->vasos_[i].puesto = (int8_t)i;
      desde = posN + 4;
    }
    servidor.send(200, "application/json", "{\"ok\":true}");
  });

  servidor.on("/api/pose", HTTP_POST, []() {
    const String cuerpo = servidor.arg("plain");
    const int pos = cuerpo.indexOf("S:");
    if (pos < 0) { servidor.send(400, "application/json", "{\"ok\":false}"); return; }
    char linea[40];
    cuerpo.substring(pos).toCharArray(linea, sizeof(linea));
    int16_t s[N_CANALES];
    const bool ok = Protocolo::leerTrama(linea, s);
    servidor.send(ok ? 200 : 400, "application/json", ok ? "{\"ok\":true}" : "{\"ok\":false}");
  });
}

void Comms::procesarLinea(char *linea) {
  if (linea[0] == '\0') return;

  if (linea[0] == 'S' && linea[1] == ':') {          // pose directa, modo manual
    int16_t s[N_CANALES];
    if (!Protocolo::leerTrama(linea, s)) { Serial.println(F("ERR trama")); return; }
    float q[N_JUNTAS] = {(float)s[0] - 90.0f, (float)s[1], -(float)s[2],
                         (float)s[3] - 120.0f, (float)s[4] - 90.0f};
    bus_.comandar(q, (float)s[5] / 90.0f * PINZA_MAX_MM);
    Serial.println(F("OK"));
    return;
  }

  if (strncmp(linea, "ORDEN:", 6) == 0) {            // ORDEN:valor,asc
    char *coma = strchr(linea + 6, ',');
    const int8_t sentido = (coma && strncmp(coma + 1, "desc", 4) == 0) ? -1 : 1;
    if (coma) *coma = '\0';
    const bool ok = sec_.iniciar(vasos_, criterioDeTexto(linea + 6), sentido);
    Serial.println(ok ? F("OK") : F("ERR plan"));
    return;
  }

  if (strncmp(linea, "VASOS:", 6) == 0) {            // VASOS:500x12,100x30,...
    char *p = linea + 6;
    for (uint8_t i = 0; i < N_PUESTOS && p && *p; i++) {
      vasos_[i].denominacion = (uint16_t)strtol(p, &p, 10);
      if (*p == 'x') p++;
      vasos_[i].monedas = (uint8_t)strtol(p, &p, 10);
      vasos_[i].zona = ZONA_ENTRADA;
      vasos_[i].puesto = (int8_t)i;
      if (*p == ',') p++;
    }
    Serial.println(F("OK"));
    return;
  }

  if (strcmp(linea, "ESTADO") == 0) {
    char json[768];
    estadoJson(json, sizeof(json));
    Serial.println(json);
    return;
  }
  if (strcmp(linea, "HOME") == 0) { sec_.irAReposo(); Serial.println(F("OK")); return; }
  if (strcmp(linea, "STOP") == 0) { sec_.detener(); Serial.println(F("OK")); return; }
  if (strcmp(linea, "PAUSA") == 0) { sec_.pausar(true); Serial.println(F("OK")); return; }
  if (strcmp(linea, "SIGUE") == 0) { sec_.pausar(false); Serial.println(F("OK")); return; }
  if (strcmp(linea, "TORQUE0") == 0) { bus_.habilitar(false); Serial.println(F("OK")); return; }
  if (strcmp(linea, "TORQUE1") == 0) { bus_.habilitar(true); Serial.println(F("OK")); return; }

  Serial.println(F("ERR comando"));
}

void Comms::atender() {
  if (wifi_) servidor.handleClient();

  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      buf_[largo_] = '\0';
      procesarLinea(buf_);
      largo_ = 0;
    } else if (largo_ < sizeof(buf_) - 1) {
      buf_[largo_++] = c;
    }
  }
}
