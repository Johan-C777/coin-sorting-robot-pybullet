#pragma once
// Interfaz entre la máquina de estados y el hardware. En el ESP32 la implementa
// src/hal/PlantaESP32; en las pruebas del PC, una planta simulada.
#include <stdint.h>

namespace seq {

enum class Barrera : uint8_t { B1 = 0, B2 = 1 };
enum class Flanco : uint8_t { Entra = 0, Sale = 1 };   // Entra = la moneda corta el haz

struct EventoBarrera {
  Barrera barrera;
  Flanco flanco;
  uint32_t t_us;   // marca de tiempo tomada en la ISR
};

struct LecturaColor {
  float razon;     // (R+G)/2B
  uint32_t total;  // R+G+B: brillo, para quedarse con la moneda centrada
};

class Planta {
 public:
  virtual ~Planta() = default;
  // Tolva (28BYJ-48): avanza n bolsillos (negativo = atrás). No bloquea.
  virtual void tolvaAvanzar(float bolsillos) = 0;
  virtual bool tolvaOcupada() const = 0;
  // Compuerta (SG90)
  virtual void compuerta(bool abierta) = 0;
  // Banda (etapa 2): pone el vaso (0..8) o la rampa de rechazo (-1) bajo el embudo. No bloquea.
  virtual void cartuchoA(int8_t vaso) = 0;
  virtual bool cartuchoOcupado() const = 0;
  // Barreras IR: saca el siguiente evento de la cola de la ISR. false si no hay.
  virtual bool siguienteEvento(EventoBarrera &ev) = 0;
  virtual void descartarEventos() = 0;
  // TCS3200: una muestra R, G, B (≈ 13 ms con ventanas de 4 ms).
  virtual LecturaColor leerColor() = 0;
  // Paro: suelta la tolva, cierra la compuerta, detiene la banda.
  virtual void detenerTodo() = 0;
};

}  // namespace seq
