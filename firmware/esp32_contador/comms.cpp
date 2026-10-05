#include "comms.h"

#include <Arduino.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <WiFi.h>

#include <stdlib.h>
#include <string.h>

namespace {
WebServer servidor(80);
Comms *instancia = nullptr;
}  // namespace

void Comms::iniciarSerie(unsigned long baudios) {
  Serial.begin(baudios);
  instancia = this;
  Serial.println(F("contador de monedas listo"));
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
  char cuerpo[512];
  conteo_.json(cuerpo, sizeof(cuerpo));
  snprintf(destino, capacidad,
           "{\"etapa\":1,\"alimentando\":%s,\"banda\":%s,\"conteo\":%s}",
           dosificador_.activo() ? "true" : "false",
           banda_.enMarcha() ? "true" : "false", cuerpo);
}

bool Comms::enviarAlBrazo(const char *ipBrazo) {
  if (!wifi_) {                       // sin red, al menos se deja la trama en el serie
    char trama[96];
    conteo_.trama(trama, sizeof(trama));
    Serial.println(trama);
    return false;
  }
  char cuerpo[512];
  conteo_.json(cuerpo, sizeof(cuerpo));
  HTTPClient http;
  char url[64];
  snprintf(url, sizeof(url), "http://%s/api/vasos", ipBrazo);
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  const int codigo = http.POST((uint8_t *)cuerpo, strlen(cuerpo));
  http.end();
  Serial.print(F("POST /api/vasos -> "));
  Serial.println(codigo);
  return codigo == 200;
}

void Comms::anunciarMoneda(int8_t canal) {
  if (canal < 0) return;
  Serial.print(F("M:"));
  Serial.print(DENOMINACION[canal]);
  Serial.print(',');
  Serial.println(canal + 1);
}

void Comms::rutasHttp() {
  servidor.on("/api/estado", HTTP_GET, []() {
    char json[768];
    instancia->estadoJson(json, sizeof(json));
    servidor.send(200, "application/json", json);
  });
  servidor.on("/api/arrancar", HTTP_POST, []() {
    const String cuerpo = servidor.arg("plain");
    const int pos = cuerpo.indexOf("ritmo");
    const float ritmo = pos >= 0 ? cuerpo.substring(pos + 7).toFloat() : 3.0f;
    instancia->dosificador_.ritmo(ritmo);
    servidor.send(200, "application/json", "{\"ok\":true}");
  });
  servidor.on("/api/detener", HTTP_POST, []() {
    instancia->dosificador_.ritmo(0);
    instancia->banda_.detener();
    servidor.send(200, "application/json", "{\"ok\":true}");
  });
  servidor.on("/api/reiniciar", HTTP_POST, []() {
    instancia->conteo_.reiniciar();
    servidor.send(200, "application/json", "{\"ok\":true}");
  });
}

void Comms::procesarLinea(char *linea) {
  if (linea[0] == '\0') return;

  if (strncmp(linea, "ALIM:", 5) == 0) {          // ALIM:3.5 monedas por segundo
    dosificador_.ritmo(atof(linea + 5));
    Serial.println(F("OK"));
    return;
  }
  if (strncmp(linea, "BANDA:", 6) == 0) {         // BANDA:0.6
    banda_.avanzar(atof(linea + 6));
    Serial.println(F("OK"));
    return;
  }
  if (strcmp(linea, "PARAR") == 0) {
    dosificador_.ritmo(0);
    banda_.detener();
    Serial.println(F("OK"));
    return;
  }
  if (strcmp(linea, "CONTEO") == 0) {
    char trama[96];
    conteo_.trama(trama, sizeof(trama));
    Serial.println(trama);
    return;
  }
  if (strcmp(linea, "ESTADO") == 0) {
    char json[768];
    estadoJson(json, sizeof(json));
    Serial.println(json);
    return;
  }
  if (strcmp(linea, "REINICIAR") == 0) {
    conteo_.reiniciar();
    Serial.println(F("OK"));
    return;
  }
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
