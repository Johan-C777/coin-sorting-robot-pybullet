#pragma once
// Comunicación de la etapa 1: puerto serie para banco y Wi-Fi para la app y
// para entregarle el lote al ESP32 del brazo.
#include "banda.h"
#include "conteo.h"
#include "dosificador.h"

class Comms {
 public:
  Comms(Conteo &conteo, Dosificador &dosificador, Banda &banda)
      : conteo_(conteo), dosificador_(dosificador), banda_(banda) {}

  void iniciarSerie(unsigned long baudios = 115200);
  bool iniciarWifi(const char *ssid, const char *clave, uint16_t segundos = 15);
  void atender();
  void estadoJson(char *destino, size_t capacidad) const;
  bool enviarAlBrazo(const char *ipBrazo);     // POST /api/vasos
  void anunciarMoneda(int8_t canal);           // "M:500,4" por el serie

 private:
  void procesarLinea(char *linea);
  void rutasHttp();

  Conteo &conteo_;
  Dosificador &dosificador_;
  Banda &banda_;
  char buf_[80];
  uint8_t largo_ = 0;
  bool wifi_ = false;
};
