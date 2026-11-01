// Pruebas del clasificador en el PC:  pio test -e native
#include <unity.h>

#include "../sintetico.h"
#include "Calibrador.h"
#include "Clasificador.h"
#include "Monedas.h"

using namespace clasif;
using namespace monedas;

static Calibracion cal;

void setUp() {
  cal = {24.0f, 10.0f, 0.0f, 0.60f, 0.05f, 1.30f, 50.0f, 2000.0f, -2000.0f, 9810.0f};
}
void tearDown() {}

void test_cuerda_y_diametro_son_inversas() {
  for (uint8_t i = 0; i < N_VASOS; i++) {
    const float d = TIPOS[i].diametro_mm;
    TEST_ASSERT_FLOAT_WITHIN(1e-3f, d, diametroDesdeCuerda(cuerdaDesdeDiametro(d, 10.0f), 10.0f));
  }
}

void test_medir_recupera_el_diametro_de_las_nueve_monedas() {
  for (uint8_t i = 0; i < N_VASOS; i++) {
    const Medicion m = medir(sintetico::moneda(TIPOS[i].diametro_mm), cal);
    TEST_ASSERT_EQUAL_UINT8((uint8_t)Motivo::Ok, (uint8_t)m.motivo);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, TIPOS[i].diametro_mm, m.diametro_mm);
    TEST_ASSERT_FLOAT_WITHIN(20.0f, 2450.0f, m.a_mm_s2);
  }
}

void test_medir_sin_aceleracion_y_con_ancho_de_haz() {
  cal.ancho_haz_mm = 1.2f;
  const Medicion m = medir(sintetico::moneda(22.4, 10.0, 1.2, 24.0, 450.0, 0.0), cal);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Motivo::Ok, (uint8_t)m.motivo);
  TEST_ASSERT_FLOAT_WITHIN(0.02f, 22.4f, m.diametro_mm);
}

void test_flancos_fuera_de_orden_y_velocidad_imposible() {
  Tiempos t = sintetico::moneda(20.3);
  t.sal1_us = t.ent1_us - 10;
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Motivo::OrdenTiempos, (uint8_t)medir(t, cal).motivo);
  const Tiempos lenta = sintetico::moneda(20.3, 10, 0, 24, 5.0, 0.0);   // 5 mm/s
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Motivo::Velocidad, (uint8_t)medir(lenta, cal).motivo);
}

void test_cada_diametro_nominal_va_a_su_vaso() {
  for (uint8_t i = 0; i < N_VASOS; i++) {
    const Decision d = decidirPorDiametro(TIPOS[i].diametro_mm, cal);
    const uint8_t esperado = (i == V_N500) ? V_A500 : i;   // las dos $500 las separa el color
    TEST_ASSERT_EQUAL_INT8(esperado, d.vaso);
  }
}

void test_tolerancia_por_clase_respeta_al_vecino() {
  // $200 nueva (22,4) y $100 antigua (23,0) están a 0,6 mm: tolerancia 0,3 - 0,05 = 0,25
  TEST_ASSERT_FLOAT_WITHIN(1e-4f, 0.25f, tolerancia(V_N200, cal));
  TEST_ASSERT_EQUAL_INT8(V_N200, decidirPorDiametro(22.4f + 0.24f, cal).vaso);
  TEST_ASSERT_EQUAL_INT8(VASO_RECHAZO, decidirPorDiametro(22.4f + 0.26f, cal).vaso);
  // $50 nueva (17,0) está lejos de todas: la limita tolerancia_max
  TEST_ASSERT_FLOAT_WITHIN(1e-4f, 0.60f, tolerancia(V_N50, cal));
  TEST_ASSERT_EQUAL_INT8(VASO_RECHAZO, decidirPorDiametro(30.0f, cal).vaso);
}

void test_color_separa_las_500_y_rechaza_la_1000_antigua() {
  Decision d = decidirPorDiametro(23.7f, cal);
  TEST_ASSERT_TRUE(d.requiere_color);
  TEST_ASSERT_EQUAL_INT8(V_N500, decidirConColor(d, 1.6f, cal).vaso);
  TEST_ASSERT_EQUAL_INT8(V_A500, decidirConColor(d, 1.0f, cal).vaso);

  d = decidirPorDiametro(DIAMETRO_A1000_MM, cal);     // cae en la clase de la $50 antigua
  TEST_ASSERT_EQUAL_INT8(V_A50, d.vaso);
  const Decision dorada = decidirConColor(d, 1.6f, cal);
  TEST_ASSERT_EQUAL_INT8(VASO_RECHAZO, dorada.vaso);
  TEST_ASSERT_EQUAL_UINT8((uint8_t)Motivo::FueraCirculacion, (uint8_t)dorada.motivo);
  TEST_ASSERT_EQUAL_INT8(V_A50, decidirConColor(d, 1.0f, cal).vaso);
}

void test_calibrador_encuentra_altura_y_ancho_del_haz() {
  const double h_real = 9.3, w_real = 0.8;
  Calibrador k;
  const uint8_t tipos[] = {V_N50, V_N100, V_N200, V_A200, V_N1000};
  for (uint8_t v : tipos)
    for (int rep = 0; rep < 3; rep++) {
      const float c = cuerdaDesdeDiametro(TIPOS[v].diametro_mm, (float)h_real) + (float)w_real;
      TEST_ASSERT_TRUE(k.agregar(c, TIPOS[v].diametro_mm));
    }
  const Calibrador::Ajuste a = k.ajustar();
  TEST_ASSERT_TRUE(a.valido);
  TEST_ASSERT_FLOAT_WITHIN(0.02f, (float)h_real, a.h_mm);
  TEST_ASSERT_FLOAT_WITHIN(0.02f, (float)w_real, a.ancho_mm);
  TEST_ASSERT_TRUE(a.rms_diametro_mm < 0.02f);
  Calibrador::aplicar(a, cal);
  TEST_ASSERT_FLOAT_WITHIN(0.02f, (float)h_real, cal.h_haz_mm);
}

void test_calibrador_pide_dos_tipos_de_moneda() {
  Calibrador k;
  for (int i = 0; i < 8; i++) k.agregar(20.0f, 20.3f);
  TEST_ASSERT_FALSE(k.ajustar().valido);
}

int main(int, char **) {
  UNITY_BEGIN();
  RUN_TEST(test_cuerda_y_diametro_son_inversas);
  RUN_TEST(test_medir_recupera_el_diametro_de_las_nueve_monedas);
  RUN_TEST(test_medir_sin_aceleracion_y_con_ancho_de_haz);
  RUN_TEST(test_flancos_fuera_de_orden_y_velocidad_imposible);
  RUN_TEST(test_cada_diametro_nominal_va_a_su_vaso);
  RUN_TEST(test_tolerancia_por_clase_respeta_al_vecino);
  RUN_TEST(test_color_separa_las_500_y_rechaza_la_1000_antigua);
  RUN_TEST(test_calibrador_encuentra_altura_y_ancho_del_haz);
  RUN_TEST(test_calibrador_pide_dos_tipos_de_moneda);
  return UNITY_END();
}
