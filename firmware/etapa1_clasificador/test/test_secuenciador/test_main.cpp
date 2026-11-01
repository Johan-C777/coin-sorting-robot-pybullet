// Pruebas de la máquina de estados con una planta simulada:  pio test -e native
#include <unity.h>

#include "../sintetico.h"
#include "Secuenciador.h"

using namespace seq;
using namespace monedas;

// ---- Planta simulada -----------------------------------------------------------------
struct PlantaFalsa : Planta {
  EventoBarrera cola[32];
  uint8_t ini = 0, fin = 0;
  int tolva_ciclos = 0;          // vueltas de actualizar() que la tolva sigue ocupada
  float tolva_total = 0;
  int retrocesos = 0;
  bool abierta = false;
  int aperturas = 0;
  int8_t vaso_banda = 99;
  float razon = 1.0f;
  int paros = 0;

  void tolvaAvanzar(float n) override { tolva_total += n; if (n < 0) retrocesos++; tolva_ciclos = 3; }
  bool tolvaOcupada() const override { return tolva_ciclos > 0; }
  void compuerta(bool a) override { if (a && !abierta) aperturas++; abierta = a; }
  void cartuchoA(int8_t v) override { vaso_banda = v; }
  bool cartuchoOcupado() const override { return false; }
  bool siguienteEvento(EventoBarrera &ev) override {
    if (ini == fin) return false;
    ev = cola[ini++ % 32];
    return true;
  }
  void descartarEventos() override { ini = fin; }
  LecturaColor leerColor() override { return {razon, 1000}; }
  void detenerTodo() override { paros++; abierta = false; }

  void evento(Barrera b, Flanco f, uint32_t t) { cola[fin++ % 32] = {b, f, t}; }
  void moneda(double D) {        // los cuatro flancos de una moneda, en orden temporal
    const clasif::Tiempos t = sintetico::moneda(D);
    EventoBarrera e[4] = {{Barrera::Primera, Flanco::Entra, t.ent1_us}, {Barrera::Primera, Flanco::Sale, t.sal1_us},
                          {Barrera::Segunda, Flanco::Entra, t.ent2_us}, {Barrera::Segunda, Flanco::Sale, t.sal2_us}};
    for (int i = 0; i < 4; i++)                         // ordenar por tiempo (B2 puede entrar antes de que B1 salga)
      for (int j = i + 1; j < 4; j++)
        if (e[j].t_us < e[i].t_us) { EventoBarrera x = e[i]; e[i] = e[j]; e[j] = x; }
    for (auto &x : e) evento(x.barrera, x.flanco, x.t_us);
  }
};

static const clasif::Calibracion CAL = {24.0f, 10.0f, 0.0f, 0.60f, 0.05f, 1.30f, 50.0f, 2000.0f, -2000.0f, 9810.0f};
static const Temporizacion T = {1800, 1500, 150, 500, 350, 250, 150, 8, 1, 0.25f};

static PlantaFalsa *p;
static Secuenciador *s;
static uint32_t ahora;

static void correr(uint32_t ms) {          // avanza el reloj de 10 en 10 ms
  for (uint32_t k = 0; k < ms; k += 10) {
    ahora += 10;
    if (p->tolva_ciclos > 0) p->tolva_ciclos--;
    s->actualizar(ahora);
  }
}

void setUp() {
  p = new PlantaFalsa();
  s = new Secuenciador(*p, CAL, T);
  ahora = 0;
}
void tearDown() { delete s; delete p; }

void test_ciclo_completo_de_una_200_nueva() {
  s->unCiclo();
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::Alimentando, (uint8_t)s->estado());
  correr(100);
  p->moneda(22.4);
  correr(2000);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::Reposo, (uint8_t)s->estado());
  TEST_ASSERT_EQUAL_INT8(V_N200, p->vaso_banda);
  TEST_ASSERT_EQUAL_INT(1, p->aperturas);
  TEST_ASSERT_FALSE(p->abierta);
  TEST_ASSERT_EQUAL_UINT16(1, s->cuenta(V_N200));
  TEST_ASSERT_EQUAL_UINT32(1, s->total());
}

void test_la_500_dorada_pasa_por_el_sensor_de_color() {
  p->razon = 1.7f;
  s->unCiclo();
  correr(50);
  p->moneda(23.7);
  correr(30);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::LeyendoColor, (uint8_t)s->estado());
  correr(2000);
  TEST_ASSERT_EQUAL_UINT16(1, s->cuenta(V_N500));
  TEST_ASSERT_FLOAT_WITHIN(1e-3f, 1.7f, s->ultimo().razon_color);
}

void test_tolva_vacia_tras_ocho_bolsillos_y_desatasco() {
  s->marcha();
  correr(60000);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::TolvaVacia, (uint8_t)s->estado());
  TEST_ASSERT_FALSE(s->automatico());
  TEST_ASSERT_EQUAL_INT(8, p->retrocesos);           // un reintento por bolsillo
  TEST_ASSERT_FLOAT_WITHIN(1e-3f, 8.0f, p->tolva_total);
}

void test_atasco_en_la_pista_detiene_todo_y_se_rearma() {
  s->unCiclo();
  correr(50);
  p->evento(Barrera::Primera, Flanco::Entra, 5000000);     // entra y nunca sale
  correr(2000);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::Falla, (uint8_t)s->estado());
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Falla::AtascoPista, (uint8_t)s->falla());
  TEST_ASSERT_EQUAL_INT(1, p->paros);
  s->reset();
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Estado::Reposo, (uint8_t)s->estado());
}

void test_dos_monedas_pegadas_van_a_rechazo() {
  s->unCiclo();
  correr(50);
  const clasif::Tiempos t = sintetico::moneda(20.3);
  p->evento(Barrera::Primera, Flanco::Entra, t.ent1_us);
  p->evento(Barrera::Primera, Flanco::Sale, t.sal1_us);
  p->evento(Barrera::Primera, Flanco::Entra, t.sal1_us + 2000);   // la segunda, detrás
  p->evento(Barrera::Segunda, Flanco::Entra, t.ent2_us);
  p->evento(Barrera::Segunda, Flanco::Sale, t.sal2_us);
  correr(2000);
  TEST_ASSERT_EQUAL_INT8(VASO_RECHAZO, p->vaso_banda);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)clasif::Motivo::DobleMoneda, (uint8_t)s->ultimo().motivo);
  TEST_ASSERT_EQUAL_UINT16(1, s->rechazos());
}

void test_vaso_lleno_desvia_a_rechazo_y_pausa() {
  for (uint16_t i = 0; i < CAPACIDAD_VASO; i++) {
    s->unCiclo();
    correr(50);
    p->moneda(17.0);
    correr(1500);
  }
  TEST_ASSERT_EQUAL_UINT16(CAPACIDAD_VASO, s->cuenta(V_N50));
  s->unCiclo();
  correr(50);
  p->moneda(17.0);
  correr(1500);
  TEST_ASSERT_EQUAL_INT8(VASO_RECHAZO, p->vaso_banda);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Falla::VasoLleno, (uint8_t)s->falla());
  s->vaciarVaso(V_N50);
  s->reset();
  TEST_ASSERT_EQUAL_UINT16(0, s->cuenta(V_N50));
}

void test_paro_de_emergencia() {
  s->marcha();
  correr(30);
  s->paro();
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Falla::Paro, (uint8_t)s->falla());
  TEST_ASSERT_FALSE(s->automatico());
  s->marcha();                                        // no arranca en falla
  TEST_ASSERT_FALSE(s->automatico());
}

int main(int, char **) {
  UNITY_BEGIN();
  RUN_TEST(test_ciclo_completo_de_una_200_nueva);
  RUN_TEST(test_la_500_dorada_pasa_por_el_sensor_de_color);
  RUN_TEST(test_tolva_vacia_tras_ocho_bolsillos_y_desatasco);
  RUN_TEST(test_atasco_en_la_pista_detiene_todo_y_se_rearma);
  RUN_TEST(test_dos_monedas_pegadas_van_a_rechazo);
  RUN_TEST(test_vaso_lleno_desvia_a_rechazo_y_pausa);
  RUN_TEST(test_paro_de_emergencia);
  return UNITY_END();
}
