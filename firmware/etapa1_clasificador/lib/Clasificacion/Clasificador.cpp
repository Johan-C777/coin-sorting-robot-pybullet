#include "Clasificador.h"

#include <math.h>

namespace clasif {

const char *texto(Motivo m) {
  switch (m) {
    case Motivo::Ok: return "ok";
    case Motivo::OrdenTiempos: return "orden de flancos";
    case Motivo::Velocidad: return "velocidad";
    case Motivo::Aceleracion: return "aceleracion";
    case Motivo::Cuerda: return "cuerda";
    case Motivo::SinCoincidencia: return "sin coincidencia";
    case Motivo::FueraCirculacion: return "fuera de circulacion";
    case Motivo::DobleMoneda: return "doble moneda";
    case Motivo::Atasco: return "atasco";
  }
  return "?";
}

float diametroDesdeCuerda(float c, float h) { return h + c * c / (4.0f * h); }

float cuerdaDesdeDiametro(float d, float h) {
  const float k = h * (d - h);
  return k > 0 ? 2.0f * sqrtf(k) : 0.0f;
}

Medicion medir(const Tiempos &t, const Calibracion &cal) {
  Medicion m{Motivo::Ok, 0, 0, 0, 0};
  // Diferencias con signo: soportan el desborde de micros() (≈ 71 min).
  const int32_t dT = (int32_t)(t.ent2_us - t.ent1_us);
  const int32_t d1 = (int32_t)(t.sal1_us - t.ent1_us);
  const int32_t d2 = (int32_t)(t.sal2_us - t.ent2_us);
  if (dT <= 0 || d1 <= 0 || d2 <= 0) { m.motivo = Motivo::OrdenTiempos; return m; }

  // Sistema 2x2 en (v0, a) restando la 2.ª ecuación de la 3.ª; luego c de la 2.ª.
  const double L = cal.sep_barreras_mm;
  const double T = dT * 1e-6, t1 = d1 * 1e-6, t3 = T + d2 * 1e-6;
  const double A = T, B = 0.5 * T * T, C = t3 - t1, D = 0.5 * (t3 * t3 - t1 * t1);
  const double det = A * D - B * C;
  if (fabs(det) < 1e-15) { m.motivo = Motivo::OrdenTiempos; return m; }
  const double v0 = L * (D - B) / det;
  const double a = L * (A - C) / det;
  const double c = v0 * t1 + 0.5 * a * t1 * t1;

  m.v0_mm_s = (float)v0;
  m.a_mm_s2 = (float)a;
  m.cuerda_mm = (float)c - cal.ancho_haz_mm;
  const double v_media = L / T;
  if (v_media < cal.v_min_mm_s || v_media > cal.v_max_mm_s || v0 <= 0) { m.motivo = Motivo::Velocidad; return m; }
  if (a < cal.a_min_mm_s2 || a > cal.a_max_mm_s2) { m.motivo = Motivo::Aceleracion; return m; }
  if (m.cuerda_mm <= 0 || m.cuerda_mm > 40.0f) { m.motivo = Motivo::Cuerda; return m; }
  m.diametro_mm = diametroDesdeCuerda(m.cuerda_mm, cal.h_haz_mm);
  return m;
}

float tolerancia(uint8_t v, const Calibracion &cal) {
  using namespace monedas;
  const float d = TIPOS[v].diametro_mm;
  float vecino = 1e9f;
  for (uint8_t j = 0; j < N_VASOS; j++) {
    const float g = fabsf(TIPOS[j].diametro_mm - d);
    if (g > 0.01f && g < vecino) vecino = g;   // la otra $500 mide lo mismo: no es vecina
  }
  const float t = vecino / 2 - cal.margen_vecino_mm;
  return t < cal.tolerancia_max_mm ? t : cal.tolerancia_max_mm;
}

Decision decidirPorDiametro(float D, const Calibracion &cal) {
  using namespace monedas;
  Decision r{VASO_RECHAZO, Motivo::SinCoincidencia, 1e9f, 0, false};
  for (uint8_t i = 0; i < N_VASOS; i++) {
    if (i == V_N500) continue;                   // mismo diámetro que A500: decide el color
    const float e = fabsf(D - TIPOS[i].diametro_mm);
    if (e < r.error_mm) { r.error_mm = e; r.vaso = (int8_t)i; }
  }
  r.tolerancia_mm = tolerancia((uint8_t)r.vaso, cal);
  if (r.error_mm > r.tolerancia_mm) { r.vaso = VASO_RECHAZO; return r; }
  r.motivo = Motivo::Ok;
  r.requiere_color = (r.vaso == V_A500 || r.vaso == V_A50);
  return r;
}

Decision decidirConColor(Decision d, float razon, const Calibracion &cal) {
  using namespace monedas;
  if (!d.requiere_color) return d;
  const bool dorada = razon > cal.umbral_dorado;
  if (d.vaso == V_A500) d.vaso = dorada ? V_N500 : V_A500;
  else if (d.vaso == V_A50 && dorada) { d.vaso = VASO_RECHAZO; d.motivo = Motivo::FueraCirculacion; }
  d.requiere_color = false;
  return d;
}

}  // namespace clasif
