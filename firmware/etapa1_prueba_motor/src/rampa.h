#pragma once
// Generador de pasos con rampa trapezoidal/triangular para cualquier motor.
// v(i) = min(vmax, sqrt(v0² + 2·a·pasos_hechos), sqrt(v0² + 2·a·pasos_restantes)):
// arranca y se detiene a v0 (frecuencia de enganche del motor), acelera lo máximo que
// permite el motor y frena a tiempo para no pasarse. Se llama a run() desde una tarea
// dedicada; ir()/parar() se pueden llamar desde otro núcleo.
#include <Arduino.h>
#include <math.h>

class Rampa {
 public:
  using Salida = void (*)(int dir);   // da un paso en la dirección dir (+1/-1)
  using Soltar = void (*)();          // suelta bobinas (opcional)

  Rampa(Salida paso, Soltar soltar = nullptr) : paso_(paso), soltar_(soltar) {}

  float v0 = 180, vmax = 800, acc = 2500;
  uint32_t pre_us = 0, post_us = 0;   // espera antes del 1er paso / antes de soltar

  void ir(long destino) {
    portENTER_CRITICAL(&mux_);
    if (destino != pos_) {
      inicio_ = pos_;
      destino_ = destino;
      dir_ = destino > pos_ ? 1 : -1;
      t_ = micros() + pre_us;
      iv_ = (uint32_t)(1e6f / v0);
      moviendo_ = true;
      if (pre_us && energizar_) energizar_();
    }
    portEXIT_CRITICAL(&mux_);
  }
  void mover(long n) { ir(destino_actual() + n); }
  void parar() {
    portENTER_CRITICAL(&mux_);
    destino_ = pos_;
    portEXIT_CRITICAL(&mux_);
  }
  bool ocupado() const { return moviendo_ || post_pend_; }
  long pos() const { return pos_; }
  void cero(long p = 0) { portENTER_CRITICAL(&mux_); pos_ = destino_ = p; portEXIT_CRITICAL(&mux_); }
  void alEnergizar(void (*f)()) { energizar_ = f; }

  void run() {
    portENTER_CRITICAL(&mux_);
    const uint32_t ahora = micros();
    if (moviendo_) {
      if (pos_ == destino_) {                       // llegó (o se pidió parar)
        moviendo_ = false;
        if (soltar_) { post_pend_ = true; t_fin_ = ahora; }
      } else if ((int32_t)(ahora - t_) >= 0) {
        paso_(dir_);
        pos_ += dir_;
        const float hechos = labs(pos_ - inicio_), faltan = labs(destino_ - pos_);
        float v = vmax;
        const float va = sqrtf(v0 * v0 + 2 * acc * hechos);
        const float vd = sqrtf(v0 * v0 + 2 * acc * faltan);
        if (va < v) v = va;
        if (vd < v) v = vd;
        iv_ = (uint32_t)(1e6f / v);
        t_ += iv_;
        if ((int32_t)(ahora - t_) > (int32_t)iv_) t_ = ahora;   // no acumular retraso
      }
    } else if (post_pend_ && (ahora - t_fin_) >= post_us) {
      post_pend_ = false;
      soltar_();
    }
    portEXIT_CRITICAL(&mux_);
  }

 private:
  long destino_actual() const { return moviendo_ ? destino_ : pos_; }
  Salida paso_;
  Soltar soltar_;
  void (*energizar_)() = nullptr;
  portMUX_TYPE mux_ = portMUX_INITIALIZER_UNLOCKED;
  volatile long pos_ = 0, destino_ = 0, inicio_ = 0;
  volatile int dir_ = 1;
  volatile bool moviendo_ = false, post_pend_ = false;
  uint32_t t_ = 0, iv_ = 5000, t_fin_ = 0;
};
