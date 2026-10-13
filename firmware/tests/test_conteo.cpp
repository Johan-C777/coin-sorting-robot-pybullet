// Pruebas del núcleo del firmware de la etapa 1, corriendo en el PC:
//     make -C firmware/tests
#include <cmath>
#include <cstdio>
#include <cstring>

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

  // estaciones de la familia nueva: 1 ($50), 2 ($100), 4 ($200), 6 ($500), 8 ($1.000)
  const uint8_t estNueva[N_VASOS] = {0, 1, 3, 5, 7};
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

  // monedas antiguas: $50 en la estación 3, $100 en la 5 y $200 en la 7
  c.sumar(2, 6);
  c.sumar(4, 4);
  c.sumar(6, 3);
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

  // el riel: diámetros crecientes y cada luz entre su moneda y la siguiente,
  // con al menos 0,25 mm a cada lado (lo que se puede ajustar en FDM)
  bool luces = true;
  for (uint8_t e = 0; e < N_ESTACIONES; e++) {
    if (LUZ_MM[e] < DIAMETRO_MM[e] + 0.25f) luces = false;                 // debe caer
    if (e + 1 < N_ESTACIONES && LUZ_MM[e] > DIAMETRO_MM[e + 1] - 0.25f) luces = false;  // no debe colarse
  }
  comprobar(luces, "cada luz deja pasar su moneda y retiene la siguiente");

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
