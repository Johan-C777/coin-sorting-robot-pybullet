#pragma once
// Dos canales de comunicación sobre el mismo estado:
//   * Serie a 115200: tramas "S:..." y comandos de texto (modo banco).
//   * HTTP JSON por Wi-Fi: lo que consume la app Streamlit.
#include "cups.h"
#include "sequencer.h"
#include "servo_bus.h"

class Comms {
 public:
  Comms(BusServos &bus, Secuenciador &sec, Vaso *vasos) : bus_(bus), sec_(sec), vasos_(vasos) {}

  void iniciarSerie(unsigned long baudios = 115200);
  bool iniciarWifi(const char *ssid, const char *clave, uint16_t segundos = 15);
  void atender();                                   // llamar en cada vuelta de loop()
  void estadoJson(char *destino, size_t capacidad) const;

 private:
  void procesarLinea(char *linea);
  void rutasHttp();

  BusServos &bus_;
  Secuenciador &sec_;
  Vaso *vasos_;
  char buf_[96];
  uint8_t largo_ = 0;
  bool wifi_ = false;
};
