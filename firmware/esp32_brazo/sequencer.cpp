#include "sequencer.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "kinematics.h"
#include "trajectory.h"

namespace {
void copiar(float destino[N_JUNTAS], const float origen[N_JUNTAS]) {
  for (uint8_t i = 0; i < N_JUNTAS; i++) destino[i] = origen[i];
}
}  // namespace

bool Secuenciador::iniciar(Vaso *vasos, uint8_t criterio, int8_t sentido, float velocidad) {
  if (ocupado()) return false;
  vasos_ = vasos;
  velocidad_ = (velocidad < 0.2f) ? 0.2f : velocidad;
  nMovs_ = Planificador::planificar(vasos_, criterio, sentido, movs_);
  if (nMovs_ == 0) {
    snprintf(mensaje_, sizeof(mensaje_), "los vasos ya estan en ese orden");
    estado_ = LISTO;
    return false;
  }
  indiceMov_ = 0;
  indiceEtapa_ = 0;
  volviendo_ = false;
  if (!prepararEtapa(0)) {
    estado_ = ERROR;
    return false;
  }
  estado_ = MOVIENDO;
  snprintf(mensaje_, sizeof(mensaje_), "movimiento 1 de %u", nMovs_);
  return true;
}

void Secuenciador::detener() {
  estado_ = LISTO;
  nMovs_ = 0;
  snprintf(mensaje_, sizeof(mensaje_), "detenido por el operador");
}

void Secuenciador::irAReposo() {
  if (ocupado()) return;
  volviendo_ = true;
  indiceEtapa_ = 0;
  etapa_.tipo = 0;
  etapa_.t = 0.0f;
  copiar(etapa_.q0, q_);
  copiar(etapa_.q1, Q_HOME);
  etapa_.pinza0 = etapa_.pinza1 = pinza_;
  etapa_.T = Trayectoria::duracionArticular(etapa_.q0, etapa_.q1, velocidad_);
  estado_ = MOVIENDO;
  snprintf(mensaje_, sizeof(mensaje_), "regresando a reposo");
}

bool Secuenciador::prepararEtapa(uint8_t indice) {
  const Movimiento &m = movs_[indiceMov_];
  const float yawO = Vasos::yawDe(m.zonaOrigen, m.puestoOrigen);
  const float yawD = Vasos::yawDe(m.zonaDestino, m.puestoDestino);

  float xo, yo, xd, yd;
  Cinematica::posePuesto(yawO, Z_AGARRE, xo, yo);
  Cinematica::posePuesto(yawD, Z_AGARRE, xd, yd);
  const float altoO[3] = {xo, yo, Z_SEGURA};
  const float bajoO[3] = {xo, yo, Z_AGARRE};
  const float altoD[3] = {xd, yd, Z_SEGURA};
  const float bajoD[3] = {xd, yd, Z_AGARRE + 0.25f};   // holgura al soltar

  etapa_.t = 0.0f;
  etapa_.pinza0 = pinza_;
  etapa_.pinza1 = pinza_;
  copiar(etapa_.q0, q_);

  const float *destino3 = nullptr;
  const float *origen3 = nullptr;

  switch (indice) {
    case 0: {                                        // ir sobre el origen
      ResultadoIK r = Cinematica::ik(altoO[0], altoO[1], altoO[2], CABECEO, 0.0f, q_[0]);
      if (!r.ok) return false;
      etapa_.tipo = 0;
      copiar(etapa_.q1, r.q);
      etapa_.pinza0 = etapa_.pinza1 = PINZA_ABIERTA_MM;
      etapa_.T = Trayectoria::duracionArticular(etapa_.q0, etapa_.q1, velocidad_);
      return true;
    }
    case 1: origen3 = altoO; destino3 = bajoO; etapa_.tipo = 1; break;   // bajar
    case 2:                                                             // cerrar
      etapa_.tipo = 2;
      etapa_.pinza0 = PINZA_ABIERTA_MM;
      etapa_.pinza1 = PINZA_CERRADA_MM;
      etapa_.T = 0.35f / velocidad_;
      copiar(etapa_.q1, q_);
      return true;
    case 3: origen3 = bajoO; destino3 = altoO; etapa_.tipo = 1; break;   // subir
    case 4: {                                                           // trasladar
      ResultadoIK r = Cinematica::ik(altoD[0], altoD[1], altoD[2], CABECEO, 0.0f, q_[0]);
      if (!r.ok) return false;
      etapa_.tipo = 0;
      copiar(etapa_.q1, r.q);
      etapa_.T = Trayectoria::duracionArticular(etapa_.q0, etapa_.q1, velocidad_);
      return true;
    }
    case 5: origen3 = altoD; destino3 = bajoD; etapa_.tipo = 1; break;   // bajar
    case 6:                                                             // abrir
      etapa_.tipo = 2;
      etapa_.pinza0 = PINZA_CERRADA_MM;
      etapa_.pinza1 = PINZA_ABIERTA_MM;
      etapa_.T = 0.35f / velocidad_;
      copiar(etapa_.q1, q_);
      return true;
    case 7: origen3 = bajoD; destino3 = altoD; etapa_.tipo = 1; break;   // subir libre
    default: return false;
  }

  for (uint8_t i = 0; i < 3; i++) {
    etapa_.p0[i] = origen3[i];
    etapa_.p1[i] = destino3[i];
  }
  ResultadoIK prueba = Cinematica::ik(etapa_.p1[0], etapa_.p1[1], etapa_.p1[2],
                                      CABECEO, 0.0f, q_[0]);
  if (!prueba.ok) return false;
  etapa_.T = Trayectoria::duracionLineal(etapa_.p0, etapa_.p1, velocidad_);
  return true;
}

void Secuenciador::aplicar(float s, BusServos &bus) {
  if (etapa_.tipo == 1) {                            // tramo lineal: inversa en cada paso
    float p[3];
    Trayectoria::interpolarLineal(etapa_.p0, etapa_.p1, s, p);
    ResultadoIK r = Cinematica::ik(p[0], p[1], p[2], CABECEO, 0.0f, q_[0]);
    if (!r.ok) {
      estado_ = ERROR;
      snprintf(mensaje_, sizeof(mensaje_), "trayectoria fuera del alcance");
      return;
    }
    copiar(q_, r.q);
  } else if (etapa_.tipo == 0) {
    float q[N_JUNTAS];
    Trayectoria::interpolarArticular(etapa_.q0, etapa_.q1, s, q);
    copiar(q_, q);
  }
  pinza_ = etapa_.pinza0 + (etapa_.pinza1 - etapa_.pinza0) * s;
  bus.comandar(q_, pinza_);
}

void Secuenciador::actualizar(float dt, BusServos &bus) {
  if (estado_ != MOVIENDO) return;

  etapa_.t += dt;
  const float s = Trayectoria::quintico(etapa_.t / etapa_.T);
  aplicar(s, bus);
  if (estado_ == ERROR) return;
  if (etapa_.t < etapa_.T) return;

  if (volviendo_) {                                  // terminó el regreso a reposo
    volviendo_ = false;
    estado_ = LISTO;
    snprintf(mensaje_, sizeof(mensaje_), "en reposo");
    return;
  }

  indiceEtapa_++;
  if (indiceEtapa_ < 8) {
    if (!prepararEtapa(indiceEtapa_)) {
      estado_ = ERROR;
      snprintf(mensaje_, sizeof(mensaje_), "sin solucion en la etapa %u", indiceEtapa_);
    }
    return;
  }

  // vaso entregado: se actualiza el mapa de puestos
  const Movimiento &m = movs_[indiceMov_];
  vasos_[m.vaso].zona = m.zonaDestino;
  vasos_[m.vaso].puesto = m.puestoDestino;

  indiceEtapa_ = 0;
  indiceMov_++;
  if (indiceMov_ >= nMovs_) {
    snprintf(mensaje_, sizeof(mensaje_), "clasificacion terminada");
    estado_ = LISTO;
    irAReposo();
    return;
  }
  snprintf(mensaje_, sizeof(mensaje_), "movimiento %u de %u", indiceMov_ + 1, nMovs_);
  if (!prepararEtapa(0)) {
    estado_ = ERROR;
    snprintf(mensaje_, sizeof(mensaje_), "sin solucion al iniciar el movimiento");
  }
}
