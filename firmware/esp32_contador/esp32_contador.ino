/*
  Etapa 1: selección, conteo y transporte de monedas.
  Sistema de Logística de Monedas Inteligentes (UMNG).

  Hardware: ESP32 DevKit V1, cinco barreras infrarrojas, servo SG90 en la
  paleta dosificadora y motorreductor de banda sobre puente H L298N.

  Puerto serie a 115200:
    ALIM:3.5     monedas por segundo que suelta la tolva
    BANDA:0.6    velocidad de la banda, de 0 a 1
    CONTEO       devuelve VASOS:50x24,100x20,...
    ESTADO       JSON con conteo y estado de los actuadores
    ENVIAR       manda el lote al ESP32 del brazo
    REINICIAR    pone el conteo en cero
    PARAR        detiene alimentación y banda

  Con Wi-Fi expone además GET /api/estado y POST /api/arrancar, /api/detener
  y /api/reiniciar, y hace POST /api/vasos al brazo cuando termina la tanda.
*/
#include "banda.h"
#include "comms.h"
#include "config.h"
#include "conteo.h"
#include "dosificador.h"
#include "sensores.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets_example.h"
#endif

Conteo conteo;
Dosificador dosificador;
Banda banda;
Comms comms(conteo, dosificador, banda);

uint32_t tUltimaMoneda = 0;
bool entregando = false;
uint32_t tEntrega = 0;

void setup() {
  comms.iniciarSerie(115200);
  Sensores::iniciar();
  dosificador.iniciar();
  banda.iniciar();
  comms.iniciarWifi(WIFI_SSID, WIFI_PASS);
  dosificador.ritmo(0);                       // arranca detenido, se activa con ALIM:
}

void loop() {
  comms.atender();
  dosificador.actualizar();

  const int8_t canal = Sensores::atender(conteo);
  if (canal >= 0) {
    comms.anunciarMoneda(canal);
    tUltimaMoneda = millis();
  }

  // un vaso lleno o treinta segundos sin monedas cierran la tanda
  const bool tandaLista = conteo.vasoLleno() ||
      (conteo.monedasTotal() > 0 && tUltimaMoneda && millis() - tUltimaMoneda > 30000);

  if (tandaLista && !entregando) {
    entregando = true;
    dosificador.ritmo(0);
    comms.enviarAlBrazo(IP_BRAZO);
    banda.avanzar(0.6f);                      // los vasos salen hacia el brazo
    tEntrega = millis();
  }

  if (entregando && millis() - tEntrega > 12000) {
    banda.detener();
    conteo.reiniciar();
    entregando = false;
    tUltimaMoneda = 0;
    Serial.println(F("vasos entregados, conteo reiniciado"));
  }
}
