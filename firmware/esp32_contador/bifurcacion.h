#pragma once
// Bifurcación activa de la ranura 6 ($500): TCS34725 por I2C apuntando al
// anillo perimetral y SG90 con la aguja de desvío.
//   0°  -> la aguja queda a ras del piso: $500 antigua (anillo plateado)
//   45° -> la aguja baja: $500 nueva (anillo dorado)
#include "color500.h"
#include "config.h"

class Bifurcacion {
 public:
  bool iniciar();                        // false si el TCS34725 no responde
  void actualizar();                     // en cada vuelta de loop()
  void monedaContada(int8_t estacion);   // la barrera del ducto confirma el paso
  bool sensorOk() const { return ok_; }
  Anillo ultimoAnillo() const { return ultimo_; }
  Clasificador500 &clasificador() { return clas_; }

 private:
  bool leer(LecturaColor &l);
  void aguja(uint8_t grados);
  Clasificador500 clas_;
  Anillo ultimo_ = Anillo::NINGUNO;
  uint32_t tLectura_ = 0;
  uint32_t tAbajo_ = 0;
  bool abajo_ = false;
  bool ok_ = false;
};
