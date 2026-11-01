#pragma once
// Máquina de estados del ciclo de una moneda (no bloqueante, tiempo inyectado).
//
//   REPOSO ──marcha──▶ ALIMENTANDO ──B1 entra──▶ MIDIENDO ──4 flancos──▶ (LEYENDO_COLOR) ──▶ POSICIONANDO
//     ▲                    │ tolva quieta                │ timeout: ATASCO → FALLA               │ vaso bajo el embudo
//     │                    ▼                             ▼                                        ▼
//     │              ESPERANDO_MONEDA ──timeout──▶ DESATASCANDO (atrás/adelante, 1 reintento)   SOLTANDO (compuerta abierta)
//     │                    │ 8 bolsillos vacíos                                                   │
//     │                    ▼                                                                      ▼
//     │               TOLVA_VACIA                                                             CERRANDO ──▶ REPOSO
//     └────────────── reset ◀── FALLA (atasco en la pista, vaso lleno, paro de emergencia)
#include <stdint.h>

#include "Calibracion.h"
#include "Clasificador.h"
#include "Monedas.h"
#include "Planta.h"

namespace seq {

enum class Estado : uint8_t {
  Reposo,
  Alimentando,
  EsperandoMoneda,
  Desatascando,
  Midiendo,
  LeyendoColor,
  Posicionando,
  Soltando,
  Cerrando,
  TolvaVacia,
  Falla,
};
const char *texto(Estado e);

enum class Falla : uint8_t { Ninguna, AtascoPista, VasoLleno, Paro };
const char *texto(Falla f);

struct Temporizacion {           // ms
  uint16_t espera_moneda;        // tras avanzar un bolsillo, cuánto esperar a que caiga
  uint16_t medicion_max;         // desde B1 entra hasta B2 sale
  uint16_t ventana_color;        // muestreo del TCS3200
  uint16_t llegada_compuerta;    // B2 sale -> moneda quieta sobre la compuerta
  uint16_t compuerta_abierta;
  uint16_t compuerta_cierre;
  uint16_t pausa_ciclo;          // entre monedas
  uint8_t vacios_para_parar;     // bolsillos seguidos sin moneda = tolva vacía
  uint8_t reintentos_desatasco;  // 0 = no retroceder el disco si no cae moneda
  float retroceso_bolsillos;     // desatasco: cuánto retrocede el disco
};

struct Resultado {
  uint32_t numero;               // consecutivo de la moneda
  int8_t vaso;
  clasif::Motivo motivo;
  clasif::Medicion medicion;
  float razon_color;             // 0 si no se leyó
};

class Secuenciador {
 public:
  using AlResultado = void (*)(const Resultado &, void *ctx);

  Secuenciador(Planta &p, const clasif::Calibracion &cal, const Temporizacion &t) : p_(p), cal_(cal), t_(t) {}

  // Órdenes (consola, botón o protocolo)
  void marcha() { if (est_ != Estado::Falla) { auto_ = true; vacios_ = 0; if (est_ == Estado::TolvaVacia) cambiar(Estado::Reposo, ahora_); } }
  void pausa() { auto_ = false; }
  void unCiclo() { if (est_ == Estado::Reposo || est_ == Estado::TolvaVacia) { auto_ = false; alimentar(); } }
  void paro();                    // paro de emergencia -> FALLA(Paro)
  void reset();                   // sale de FALLA y vacía contadores de error
  void vaciarVaso(int8_t v);      // el operador vació un vaso (-1 = todos)

  // Llamar en cada vuelta del loop.
  void actualizar(uint32_t ahora_ms);

  void alResultado(AlResultado f, void *ctx) { cb_ = f; ctx_ = ctx; }
  void calibracion(const clasif::Calibracion &c) { cal_ = c; }
  const clasif::Calibracion &calibracion() const { return cal_; }

  Estado estado() const { return est_; }
  Falla falla() const { return falla_; }
  bool automatico() const { return auto_; }
  uint16_t cuenta(uint8_t vaso) const { return cuenta_[vaso]; }
  uint16_t rechazos() const { return rechazos_; }
  uint32_t total() const { return numero_; }
  const Resultado &ultimo() const { return ultimo_; }

 private:
  void cambiar(Estado e, uint32_t t) { est_ = e; t_est_ = t; }
  void alimentar();
  void iniciarMedicion(uint32_t t_us);
  bool buscarEntradaB1();
  void terminarMedicion();
  void decidir(clasif::Decision d);
  void fallar(Falla f);

  Planta &p_;
  clasif::Calibracion cal_;
  Temporizacion t_;
  Estado est_ = Estado::Reposo;
  Falla falla_ = Falla::Ninguna;
  bool auto_ = false;
  uint32_t ahora_ = 0, t_est_ = 0;
  uint8_t vacios_ = 0, reintentos_ = 0, flancos_ = 0, fase_ = 0;
  bool doble_ = false, lleno_ = false;
  clasif::Tiempos tm_{};
  clasif::Decision dec_{};
  LecturaColor mejor_color_{};
  Resultado ultimo_{};
  uint16_t cuenta_[monedas::N_VASOS] = {};
  uint16_t rechazos_ = 0;
  uint32_t numero_ = 0;
  AlResultado cb_ = nullptr;
  void *ctx_ = nullptr;
};

}  // namespace seq
