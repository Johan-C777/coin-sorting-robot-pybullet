#include "Secuenciador.h"

namespace seq {

using clasif::Motivo;
using monedas::VASO_RECHAZO;

namespace {
constexpr uint8_t E1 = 1, S1 = 2, E2 = 4, S2 = 8, TODOS = E1 | S1 | E2 | S2;
}

const char *texto(Estado e) {
  switch (e) {
    case Estado::Reposo: return "REPOSO";
    case Estado::Alimentando: return "ALIMENTANDO";
    case Estado::EsperandoMoneda: return "ESPERANDO_MONEDA";
    case Estado::Desatascando: return "DESATASCANDO";
    case Estado::Midiendo: return "MIDIENDO";
    case Estado::LeyendoColor: return "LEYENDO_COLOR";
    case Estado::Posicionando: return "POSICIONANDO";
    case Estado::Soltando: return "SOLTANDO";
    case Estado::Cerrando: return "CERRANDO";
    case Estado::TolvaVacia: return "TOLVA_VACIA";
    case Estado::Falla: return "FALLA";
  }
  return "?";
}

const char *texto(Falla f) {
  switch (f) {
    case Falla::Ninguna: return "ninguna";
    case Falla::AtascoPista: return "atasco en la pista";
    case Falla::VasoLleno: return "vaso lleno";
    case Falla::Paro: return "paro de emergencia";
  }
  return "?";
}

void Secuenciador::alimentar() {
  p_.descartarEventos();
  flancos_ = 0;
  doble_ = false;
  reintentos_ = 0;
  fase_ = 0;
  p_.tolvaAvanzar(1);
  cambiar(Estado::Alimentando, ahora_);
}

void Secuenciador::iniciarMedicion(uint32_t t_us) {
  tm_ = {t_us, 0, 0, 0};
  flancos_ = E1;
  doble_ = false;
  vacios_ = 0;
  cambiar(Estado::Midiendo, ahora_);
}

// Consume eventos hasta encontrar "B1 entra". Los demás (ruido sin moneda) se ignoran.
bool Secuenciador::buscarEntradaB1() {
  EventoBarrera ev;
  while (p_.siguienteEvento(ev)) {
    if (ev.barrera == Barrera::Primera && ev.flanco == Flanco::Entra) {
      iniciarMedicion(ev.t_us);
      return true;
    }
  }
  return false;
}

void Secuenciador::paro() { fallar(Falla::Paro); }

void Secuenciador::reset() {
  if (est_ != Estado::Falla) return;
  falla_ = Falla::Ninguna;
  lleno_ = false;
  p_.compuerta(false);
  p_.descartarEventos();
  cambiar(Estado::Reposo, ahora_);
}

void Secuenciador::vaciarVaso(int8_t v) {
  for (uint8_t i = 0; i < monedas::N_VASOS; i++)
    if (v < 0 || v == (int8_t)i) cuenta_[i] = 0;
}

void Secuenciador::fallar(Falla f) {
  falla_ = f;
  auto_ = false;
  if (f != Falla::VasoLleno) p_.detenerTodo();
  cambiar(Estado::Falla, ahora_);
}

void Secuenciador::terminarMedicion() {
  const clasif::Medicion m = clasif::medir(tm_, cal_);
  ultimo_.medicion = m;
  ultimo_.razon_color = 0;
  clasif::Decision d{VASO_RECHAZO, m.motivo, 0, 0, false};
  if (doble_) d.motivo = Motivo::DobleMoneda;
  else if (m.motivo == Motivo::Ok) d = clasif::decidirPorDiametro(m.diametro_mm, cal_);
  if (d.requiere_color) {
    dec_ = d;
    mejor_color_ = {0, 0};
    cambiar(Estado::LeyendoColor, ahora_);
    return;
  }
  decidir(d);
}

void Secuenciador::decidir(clasif::Decision d) {
  int8_t vaso = d.vaso;
  if (vaso >= 0 && cuenta_[vaso] >= monedas::CAPACIDAD_VASO) {   // no se derrama: va a rechazo
    vaso = VASO_RECHAZO;
    lleno_ = true;
  }
  ultimo_.numero = ++numero_;
  ultimo_.vaso = vaso;
  ultimo_.motivo = d.motivo;
  p_.cartuchoA(vaso);
  if (cb_) cb_(ultimo_, ctx_);
  cambiar(Estado::Posicionando, ahora_);
}

void Secuenciador::actualizar(uint32_t ahora) {
  ahora_ = ahora;
  const uint32_t en_estado = ahora - t_est_;
  switch (est_) {
    case Estado::Reposo:
      if (buscarEntradaB1()) break;                       // moneda tardía: se mide igual
      if (auto_ && en_estado >= t_.pausa_ciclo) alimentar();
      break;

    case Estado::Alimentando:
      if (buscarEntradaB1()) break;
      if (!p_.tolvaOcupada()) cambiar(Estado::EsperandoMoneda, ahora);
      break;

    case Estado::EsperandoMoneda:
      if (buscarEntradaB1()) break;
      if (en_estado < t_.espera_moneda) break;
      if (reintentos_ < t_.reintentos_desatasco) {        // agitar el disco y esperar otra vez
        reintentos_++;
        fase_ = 0;
        p_.tolvaAvanzar(-t_.retroceso_bolsillos);
        cambiar(Estado::Desatascando, ahora);
      } else if (++vacios_ >= t_.vacios_para_parar) {
        auto_ = false;
        vacios_ = 0;
        cambiar(Estado::TolvaVacia, ahora);
      } else {
        cambiar(Estado::Reposo, ahora);
      }
      break;

    case Estado::Desatascando:
      if (buscarEntradaB1()) break;
      if (p_.tolvaOcupada()) break;
      if (fase_ == 0) { fase_ = 1; p_.tolvaAvanzar(t_.retroceso_bolsillos); }
      else cambiar(Estado::EsperandoMoneda, ahora);
      break;

    case Estado::Midiendo: {
      EventoBarrera ev;
      while (p_.siguienteEvento(ev)) {
        const bool b1 = ev.barrera == Barrera::Primera, entra = ev.flanco == Flanco::Entra;
        if (b1 && !entra && !(flancos_ & S1)) { tm_.sal1_us = ev.t_us; flancos_ |= S1; }
        else if (b1 && entra && (flancos_ & S1)) doble_ = true;      // otra moneda detrás
        else if (!b1 && entra && !(flancos_ & E2)) { tm_.ent2_us = ev.t_us; flancos_ |= E2; }
        else if (!b1 && !entra && (flancos_ & E2) && !(flancos_ & S2)) { tm_.sal2_us = ev.t_us; flancos_ |= S2; }
      }
      if (flancos_ == TODOS) terminarMedicion();
      else if (en_estado > t_.medicion_max) fallar(Falla::AtascoPista);
      break;
    }

    case Estado::LeyendoColor: {
      const LecturaColor l = p_.leerColor();
      if (l.total > mejor_color_.total) mejor_color_ = l;   // la más brillante = moneda centrada
      if (en_estado >= t_.ventana_color) {
        ultimo_.razon_color = mejor_color_.razon;
        decidir(clasif::decidirConColor(dec_, mejor_color_.razon, cal_));
      }
      break;
    }

    case Estado::Posicionando:
      if (en_estado >= t_.llegada_compuerta && !p_.cartuchoOcupado()) {
        p_.compuerta(true);
        cambiar(Estado::Soltando, ahora);
      }
      break;

    case Estado::Soltando:
      if (en_estado >= t_.compuerta_abierta) {
        p_.compuerta(false);
        cambiar(Estado::Cerrando, ahora);
      }
      break;

    case Estado::Cerrando:
      if (en_estado < t_.compuerta_cierre) break;
      if (ultimo_.vaso >= 0) cuenta_[ultimo_.vaso]++;
      else rechazos_++;
      if (lleno_) fallar(Falla::VasoLleno);
      else cambiar(Estado::Reposo, ahora);
      break;

    case Estado::TolvaVacia:
    case Estado::Falla:
      break;
  }
}

}  // namespace seq
