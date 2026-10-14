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
  const uint8_t estNueva[N_VASOS] = {0, 1, 3, 6, 8};
  const uint16_t lote[N_VASOS] = {24, 20, 18, 14, 12};
  for (uint8_t v = 0; v < N_VASOS; v++) c.sumar(estNueva[v], lote[v]);

  comprobar(c.monedasTotal() == 88, "cuenta las 88 monedas del lote");
  comprobar(c.valorTotal() == 25800u, "valor total de $25.800");
  comprobar(cerca(c.pesoTotal(), 507.1f, 0.2f), "peso total de 507,1 g con los cinco vasos");
  comprobar(c.valor(4) == 12000u && cerca(c.pesoG(4), 137.4f, 0.1f), "vaso de $1.000");
  comprobar(!c.vasoLleno(), "ningun vaso llego a la capacidad");

  char buf[96];
  c.trama(buf, sizeof(buf));
  comprobar(strcmp(buf, "VASOS:50x24,100x20,200x18,500x14,1000x12") == 0,
            "sin antiguas la trama no cambia");

  // monedas antiguas: $50 en el ducto 3, $100 en el 5 y $200 en el 8
  c.sumar(2, 6);
  c.sumar(4, 4);
  c.sumar(7, 3);
  comprobar(c.monedas(0) == 30 && c.antiguas(0) == 6 && c.antiguasTotal() == 13,
            "las antiguas caen en el vaso de su denominacion");
  comprobar(cerca(c.pesoG(0), 93.0f, 0.05f), "vaso de $50: 24 nuevas de 2 g y 6 antiguas de 4,5 g");
  comprobar(c.valorTotal() == 25800u + 6 * 50 + 4 * 100 + 3 * 200, "las antiguas suman su valor");
  c.trama(buf, sizeof(buf));
  comprobar(strcmp(buf, "VASOS:50x30a6,100x24a4,200x21a3,500x14,1000x12") == 0,
            "trama con antiguas que entiende el ESP32 del brazo");

  char js[768];
  const size_t largo = c.json(js, sizeof(js));
  comprobar(strstr(js, "\"den\":50,\"n\":30,\"antiguas\":6") != nullptr &&
            strstr(js, "\"antiguas\":13") != nullptr && largo < sizeof(js),
            "cuerpo JSON de POST /api/vasos");

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
                VASO_DE_ESTACION[ESTACION_A500] == VASO_DE_ESTACION[ESTACION_N500],
            "los dos ductos de $500 van al mismo vaso con su familia");

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
