#include "Calibrador.h"

#include <math.h>

#include "Clasificador.h"

namespace clasif {

bool Calibrador::agregar(float c, float d) {
  if (n_ >= MAX_MUESTRAS || c <= 0 || d <= 0) return false;
  c_[n_] = c;
  d_[n_] = d;
  n_++;
  return true;
}

uint8_t Calibrador::tiposDistintos() const {
  uint8_t k = 0;
  for (uint8_t i = 0; i < n_; i++) {
    bool nuevo = true;
    for (uint8_t j = 0; j < i; j++)
      if (fabsf(d_[j] - d_[i]) < 0.01f) { nuevo = false; break; }
    if (nuevo) k++;
  }
  return k;
}

Calibrador::Ajuste Calibrador::ajustar(float h_min, float h_max, float paso) const {
  Ajuste mejor{false, 0, 0, 0, 0};
  if (n_ < 6 || tiposDistintos() < 2) return mejor;
  float dmin = d_[0];
  for (uint8_t i = 1; i < n_; i++) dmin = fminf(dmin, d_[i]);
  if (h_max > dmin - 0.5f) h_max = dmin - 0.5f;          // el haz debe quedar bajo la moneda más chica

  double sse_min = 1e30;
  for (float h = h_min; h <= h_max; h += paso) {
    double w = 0;
    for (uint8_t i = 0; i < n_; i++) w += c_[i] - cuerdaDesdeDiametro(d_[i], h);
    w /= n_;
    double sse = 0;
    for (uint8_t i = 0; i < n_; i++) {
      const double r = c_[i] - w - cuerdaDesdeDiametro(d_[i], h);
      sse += r * r;
    }
    if (sse < sse_min) { sse_min = sse; mejor.h_mm = h; mejor.ancho_mm = (float)w; }
  }
  double s2 = 0, mx = 0;
  for (uint8_t i = 0; i < n_; i++) {
    const double e = diametroDesdeCuerda(c_[i] - mejor.ancho_mm, mejor.h_mm) - d_[i];
    s2 += e * e;
    if (fabs(e) > mx) mx = fabs(e);
  }
  mejor.rms_diametro_mm = (float)sqrt(s2 / n_);
  mejor.max_diametro_mm = (float)mx;
  mejor.valido = true;
  return mejor;
}

void Calibrador::aplicar(const Ajuste &a, Calibracion &cal) {
  if (!a.valido) return;
  cal.h_haz_mm = a.h_mm;
  cal.ancho_haz_mm = a.ancho_mm;
}

}  // namespace clasif
