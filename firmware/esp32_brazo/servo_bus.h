#pragma once
// Capa de salida: convierte poses en PWM y las suaviza con una rampa.
// Es lo único que toca el hardware, así el resto del firmware se prueba en el PC.
#include "config.h"
#include "protocol.h"

class BusServos {
 public:
  bool iniciar();                                   // I2C + PCA9685 a 50 Hz
  void comandar(const float q[N_JUNTAS], float pinzaMm);
  void actualizar(float dt);                        // rampa y escritura de PWM
  void habilitar(bool activo);                      // corta o repone el torque

  const float *pose() const { return q_; }
  float pinza() const { return pinzaMm_; }
  void trama(char *destino, uint8_t capacidad) const;

 private:
  void escribir();
  float q_[N_JUNTAS] = {0, 90, -90, -90, 0};
  float pinzaMm_ = PINZA_ABIERTA_MM;
  float objetivo_[N_CANALES] = {90, 90, 90, 30, 90, 85};   // ángulos de servo
  float actual_[N_CANALES] = {90, 90, 90, 30, 90, 85};
  bool listo_ = false;
  bool habilitado_ = true;
};
