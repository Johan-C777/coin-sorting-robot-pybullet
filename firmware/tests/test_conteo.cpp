// Pruebas del núcleo del firmware de la etapa 1, corriendo en el PC:
//     make -C firmware/tests
#include <cmath>
#include <cstdio>
#include <cstring>

#include "../esp32_contador/color500.h"
#include "../esp32_contador/conteo.h"

static int fallos = 0;
static void comprobar(bool ok, const char *nombre) {
  printf("%s %s\n", ok ? "  ok  " : "FALLO ", nombre);
  if (!ok) fallos++;
}
static bool cerca(float a, float b, float tol) { return fabsf(a - b) <= tol; }

int main() {
  printf("Pruebas del contador de monedas\n");
  Conteo c;

  comprobar(c.monedasTotal() == 0 && c.valorTotal() == 0, "arranca en cero");

  // ductos de la familia nueva: 1 ($50), 2 ($100), 4 ($200), 7 ($500), 9 ($1.000)
  const uint8_t estNueva[5] = {0, 1, 3, 6, 8};
  const uint16_t lote[5] = {24, 20, 18, 14, 12};
  for (uint8_t i = 0; i < 5; i++) c.sumar(estNueva[i], lote[i]);

  comprobar(c.monedasTotal() == 88, "cuenta las 88 monedas del lote");
  comprobar(c.valorTotal() == 25800u, "valor total de $25.800");
  comprobar(cerca(c.pesoTotal(), 507.1f, 0.2f), "peso total de 507,1 g con los cinco vasos llenos");
  comprobar(c.valor(8) == 12000u && cerca(c.pesoG(8), 137.4f, 0.1f), "vaso de $1.000 (el noveno)");
  comprobar(c.monedas(2) == 0 && c.pesoG(2) == 0.0f, "un vaso sin monedas no pesa ni cuenta");
  comprobar(!c.vasoLleno(), "ningun vaso llego a la capacidad");

  char buf[160];
  c.trama(buf, sizeof(buf));
  comprobar(strcmp(buf, "VASOS:50x24,100x20,50x0,200x18,100x0,500x0,500x14,200x0,1000x12") == 0,
            "la trama lleva los nueve vasos, en el orden de los ductos");

  // monedas antiguas: $50 en el ducto 3, $100 en el 5 y $200 en el 8
  c.sumar(2, 6);
  c.sumar(4, 4);
  c.sumar(7, 3);
  comprobar(c.monedas(0) == 24 && c.monedas(2) == 6 && c.antiguas(2) == 6 && c.antiguasTotal() == 13,
            "las antiguas caen en su propio vaso, aparte de las nuevas");
  comprobar(cerca(c.pesoG(0), 66.0f, 0.05f) && cerca(c.pesoG(2), 45.0f, 0.05f),
            "vaso de $50 nuevo: 24 de 2 g; vaso de $50 antiguo: 6 de 4,5 g");
  comprobar(c.valorTotal() == 25800u + 6 * 50 + 4 * 100 + 3 * 200, "las antiguas suman su valor");
  c.trama(buf, sizeof(buf));
  comprobar(strcmp(buf, "VASOS:50x24,100x20,50x6a6,200x18,100x4a4,500x0,500x14,200x3a3,1000x12") == 0,
            "trama con antiguas que entiende el ESP32 del brazo");

  char js[1024];
  const size_t largo = c.json(js, sizeof(js));
  comprobar(strstr(js, "\"den\":50,\"familia\":\"antigua\",\"n\":6,\"antiguas\":6") != nullptr &&
            strstr(js, "\"antiguas\":13") != nullptr && largo < sizeof(js),
            "cuerpo JSON de POST /api/vasos con los nueve vasos");

  Conteo lleno;                                   // peor caso: nueve vasos llenos de antiguas
  for (uint8_t e = 0; e < N_ESTACIONES; e++) lleno.sumar(e, MONEDAS_POR_VASO);
  char peor[1024], tramaPeor[160];
  comprobar(lleno.json(peor, sizeof(peor)) < sizeof(peor) - 1 &&
                lleno.trama(tramaPeor, sizeof(tramaPeor)) < sizeof(tramaPeor) - 1,
            "los buffers de comms.cpp alcanzan con los nueve vasos llenos");

  c.sumar(0, MONEDAS_POR_VASO);
  comprobar(c.vasoLleno(), "avisa cuando un vaso se llena");

  // el riel (scripts/generar_clasificador.py): cada moneda cae en su ranura con
  // al menos 0,4 mm de holgura y ninguna se cuela en una ranura anterior
  bool ranuras = true;
  for (uint8_t e = 0; e < N_ESTACIONES; e++) {
    const uint8_t k = RANURA_DE_ESTACION[e];
    if (RANURA_MM[k] > 0 && RANURA_MM[k] - DIAMETRO_MM[e] < 0.4f - 1e-4f) ranuras = false;
    for (uint8_t j = 0; j < k; j++)
      if (RANURA_MM[j] >= DIAMETRO_MM[e]) ranuras = false;
  }
  comprobar(ranuras, "cada ranura deja caer su moneda y retiene las mayores");
  comprobar(FAMILIA[ESTACION_A500] == ANTIGUA && FAMILIA[ESTACION_N500] == NUEVA &&
                VASO_DE_ESTACION[ESTACION_A500] != VASO_DE_ESTACION[ESTACION_N500] &&
                DENOMINACION_VASO[VASO_DE_ESTACION[ESTACION_A500]] == 500 &&
                DENOMINACION_VASO[VASO_DE_ESTACION[ESTACION_N500]] == 500,
            "las dos $500 van a vasos distintos, antigua y nueva");

  // anillo de $500: línea base oscura, luego la moneda frente al sensor
  Clasificador500 cl;
  for (int i = 0; i < 20; i++) cl.alimentar({100, 30, 30, 30});
  Anillo a1 = Anillo::NINGUNO;
  for (int i = 0; i < 6; i++) {
    const Anillo a = cl.alimentar({900, 420, 330, 230});   // dorado: R,G >> B
    if (a != Anillo::NINGUNO) a1 = a;
  }
  for (int i = 0; i < 5; i++) cl.alimentar({100, 30, 30, 30});
  Anillo a2 = Anillo::NINGUNO;
  int decisiones = 0;
  for (int i = 0; i < 6; i++) {
    const Anillo a = cl.alimentar({900, 300, 310, 290});   // plateado: equilibrado
    if (a != Anillo::NINGUNO) { a2 = a; decisiones++; }
  }
  comprobar(a1 == Anillo::DORADO && a2 == Anillo::PLATEADO && decisiones == 1,
            "anillo dorado / plateado, una decision por moneda");

  bool cubiertos = true;
  for (uint8_t v = 0; v < N_VASOS; v++) {
    bool alguno = false;
    for (uint8_t e = 0; e < N_ESTACIONES; e++) if (VASO_DE_ESTACION[e] == v) alguno = true;
    if (!alguno) cubiertos = false;
  }
  comprobar(cubiertos, "cada vaso recibe de al menos una estacion");

  printf(fallos == 0 ? "\nTodo en orden\n" : "\n%d prueba(s) fallaron\n", fallos);
  return fallos ? 1 : 0;
}
