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

  const uint16_t lote[N_CANALES] = {24, 20, 18, 14, 12};
  for (uint8_t i = 0; i < N_CANALES; i++) c.sumar(i, lote[i]);

  comprobar(c.monedasTotal() == 88, "cuenta las 88 monedas del lote");
  comprobar(c.valorTotal() == 25800u, "valor total de $25.800");
  comprobar(cerca(c.pesoTotal(), 507.1f, 0.2f), "peso total de 507,1 g con los cinco vasos");
  comprobar(c.valor(4) == 12000u && cerca(c.pesoG(4), 137.4f, 0.1f), "canal de $1.000");
  comprobar(!c.vasoLleno(), "ningun vaso llego a la capacidad");

  c.sumar(0, MONEDAS_POR_VASO);
  comprobar(c.vasoLleno(), "avisa cuando un vaso se llena");

  c.reiniciar();
  for (uint8_t i = 0; i < N_CANALES; i++) c.sumar(i, lote[i]);
  char buf[96];
  c.trama(buf, sizeof(buf));
  comprobar(strcmp(buf, "VASOS:50x24,100x20,200x18,500x14,1000x12") == 0,
            "trama que entiende el ESP32 del brazo");

  char js[512];
  c.json(js, sizeof(js));
  comprobar(strstr(js, "\"den\":500,\"n\":14") != nullptr &&
            strstr(js, "\"monedas\":88") != nullptr, "cuerpo JSON de POST /api/vasos");

  // las luces del riel deben separar sin ambigüedad
  bool luces = true;
  for (uint8_t i = 0; i < N_CANALES; i++) {
    if (LUZ_MM[i] <= DIAMETRO_MM[i] + 0.3f) luces = false;          // debe pasar
    if (i + 1 < N_CANALES && LUZ_MM[i] >= DIAMETRO_MM[i + 1] - 0.3f) luces = false;  // no debe colarse
  }
  comprobar(luces, "cada luz deja pasar su moneda y retiene la siguiente");

  printf(fallos == 0 ? "\nTodo en orden\n" : "\n%d prueba(s) fallaron\n", fallos);
  return fallos ? 1 : 0;
}
