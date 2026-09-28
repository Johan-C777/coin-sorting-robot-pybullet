#pragma once
// Máquina de estados que ejecuta el plan de clasificación.
// Los ocho tramos por vaso son los mismos de docs/02-cinematica.md.
#include "cups.h"
#include "planner.h"
#include "servo_bus.h"

class Secuenciador {
 public:
  enum Estado : uint8_t { LISTO = 0, MOVIENDO, PAUSADO, ERROR };

  bool iniciar(Vaso *vasos, uint8_t criterio, int8_t sentido, float velocidad = 1.0f);
  void actualizar(float dt, BusServos &bus);
  void pausar(bool si) { if (estado_ == MOVIENDO || estado_ == PAUSADO) estado_ = si ? PAUSADO : MOVIENDO; }
  void detener();
  void irAReposo();

  Estado estado() const { return estado_; }
  bool ocupado() const { return estado_ == MOVIENDO || estado_ == PAUSADO; }
  uint8_t paso() const { return (uint8_t)(indiceMov_ + 1); }
  uint8_t total() const { return nMovs_; }
  const char *mensaje() const { return mensaje_; }

 private:
  struct Etapa {
    uint8_t tipo;            // 0 articular, 1 lineal, 2 pinza
    float T, t;
    float q0[N_JUNTAS], q1[N_JUNTAS];
    float p0[3], p1[3];
    float pinza0, pinza1;
  };

  bool prepararEtapa(uint8_t indice);
  void aplicar(float s, BusServos &bus);

  Vaso *vasos_ = nullptr;
  Movimiento movs_[10];
  uint8_t nMovs_ = 0;
  uint8_t indiceMov_ = 0;
  uint8_t indiceEtapa_ = 0;
  Etapa etapa_;
  float velocidad_ = 1.0f;
  float q_[N_JUNTAS] = {0, 90, -90, -90, 0};
  float pinza_ = PINZA_ABIERTA_MM;
  Estado estado_ = LISTO;
  bool volviendo_ = false;
  char mensaje_[64] = "listo";
};
