#pragma once
// Implementación real de seq::Planta: une la máquina de estados (portable) con el hardware.
#include "Actuadores.h"
#include "Barreras.h"
#include "Color.h"
#include "Planta.h"

namespace hal {

class PlantaESP32 : public seq::Planta {
 public:
  explicit PlantaESP32(Color &c) : color_(c) {}
  void tolvaAvanzar(float n) override { tolvaBolsillos(n); }
  bool tolvaOcupada() const override { return hal::tolvaOcupada(); }
  void compuerta(bool a) override { hal::compuerta(a); }
  void cartuchoA(int8_t v) override { bandaVaso(v); }
  bool cartuchoOcupado() const override { return bandaOcupada(); }
  bool siguienteEvento(seq::EventoBarrera &ev) override { return barrerasEvento(ev); }
  void descartarEventos() override { barrerasDescartar(); }
  seq::LecturaColor leerColor() override { return color_.leer(); }
  void detenerTodo() override {
    tolvaParar();
    bandaParar();
    hal::compuerta(false);
  }

 private:
  Color &color_;
};

}  // namespace hal
