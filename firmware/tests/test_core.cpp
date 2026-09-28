// Pruebas del núcleo del firmware en el PC (sin Arduino):
//     make -C firmware/tests
// Comparan contra los mismos números de la memoria de cálculo y de las
// pruebas de Python, así que un cambio en un lado se detecta en el otro.
#include <cmath>
#include <initializer_list>
#include <cstdio>
#include <cstring>

#include "../esp32_brazo/cups.h"
#include "../esp32_brazo/kinematics.h"
#include "../esp32_brazo/planner.h"
#include "../esp32_brazo/protocol.h"
#include "../esp32_brazo/sequencer.h"
#include "../esp32_brazo/trajectory.h"

static int fallos = 0;

static void comprobar(bool condicion, const char *nombre) {
  printf("%s %s\n", condicion ? "  ok  " : "FALLO ", nombre);
  if (!condicion) fallos++;
}

static bool cerca(float a, float b, float tol) { return fabsf(a - b) <= tol; }

int main() {
  printf("Pruebas del nucleo del firmware\n");

  // --- cinemática directa en reposo
  float x, y, z, phi;
  Cinematica::fk(Q_HOME, x, y, z, phi);
  comprobar(cerca(x, 15.0f, 1e-3f) && cerca(y, 0.0f, 1e-3f) &&
            cerca(z, 19.0f, 1e-3f) && cerca(phi, -90.0f, 1e-3f),
            "fk en reposo da (15, 0, 19) y cabeceo -90");

  // --- cinemática inversa en el puesto R1
  float px, py;
  Cinematica::posePuesto(YAW_RACK[0], Z_AGARRE, px, py);
  ResultadoIK r = Cinematica::ik(px, py, Z_AGARRE);
  comprobar(r.ok, "ik del puesto R1 tiene solucion");
  comprobar(cerca(r.q[0], 24.00f, 0.01f) && cerca(r.q[1], 49.02f, 0.01f) &&
            cerca(r.q[2], -82.53f, 0.01f) && cerca(r.q[3], -56.50f, 0.01f),
            "ik del puesto R1 coincide con la memoria de calculo");

  // --- ida y vuelta en los diez puestos
  bool idaYVuelta = true;
  for (uint8_t zona = 0; zona < 2; zona++) {
    for (uint8_t i = 0; i < N_PUESTOS; i++) {
      const float yaw = Vasos::yawDe(zona, i);
      for (float altura : {Z_AGARRE, Z_SEGURA}) {
        Cinematica::posePuesto(yaw, altura, px, py);
        ResultadoIK s = Cinematica::ik(px, py, altura);
        if (!s.ok) { idaYVuelta = false; continue; }
        Cinematica::fk(s.q, x, y, z, phi);
        if (!cerca(x, px, 2e-3f) || !cerca(y, py, 2e-3f) || !cerca(z, altura, 2e-3f))
          idaYVuelta = false;
      }
    }
  }
  comprobar(idaYVuelta, "los diez puestos resuelven ida y vuelta a las dos alturas");

  // --- fuera del alcance y fuera de limite
  comprobar(!Cinematica::ik(40.0f, 30.0f, Z_AGARRE).ok, "punto lejano se rechaza");
  ResultadoIK lim = Cinematica::ik(2.0f, 0.0f, 2.0f);
  comprobar(!lim.ok, "pose imposible se rechaza antes de mover");

  // --- trama de servos
  char buf[32];
  Protocolo::armarTrama(Q_HOME, PINZA_ABIERTA_MM, buf, sizeof(buf));
  comprobar(strcmp(buf, "S:90,90,90,30,90,85") == 0, "trama de reposo");
  Protocolo::armarTrama(r.q, PINZA_ABIERTA_MM, buf, sizeof(buf));
  comprobar(strcmp(buf, "S:114,49,83,64,90,85") == 0, "trama del puesto R1");
  comprobar(Protocolo::microsegundos(114) == 1767 && Protocolo::microsegundos(90) == 1500,
            "anchos de pulso");
  int16_t leidos[N_CANALES];
  comprobar(Protocolo::leerTrama("S:114,49,83,64,90,85", leidos) && leidos[0] == 114 &&
            leidos[5] == 85, "lectura de trama");
  comprobar(!Protocolo::leerTrama("X:1,2,3", leidos), "trama invalida se rechaza");

  // --- perfil quintico
  comprobar(cerca(Trayectoria::quintico(0.0f), 0.0f, 1e-6f) &&
            cerca(Trayectoria::quintico(1.0f), 1.0f, 1e-6f) &&
            cerca(Trayectoria::quintico(0.5f), 0.5f, 1e-6f),
            "perfil quintico en los extremos y en el centro");
  comprobar(cerca(Trayectoria::velocidadPico(172.0f, 2.2933f), 140.6f, 0.2f) &&
            cerca(Trayectoria::aceleracionPico(172.0f, 2.2933f), 188.8f, 0.5f),
            "picos de velocidad y aceleracion");

  // --- planificador
  Vaso vasos[N_PUESTOS] = {
      {500, 12, ZONA_ENTRADA, 0}, {100, 30, ZONA_ENTRADA, 1}, {1000, 8, ZONA_ENTRADA, 2},
      {50, 25, ZONA_ENTRADA, 3}, {200, 17, ZONA_ENTRADA, 4}};
  Movimiento movs[10];
  uint8_t n = Planificador::planificar(vasos, POR_VALOR, 1, movs);
  comprobar(n == 5, "desde la entrada son cinco movimientos");
  const uint8_t esperado[5] = {3, 1, 4, 0, 2};      // 50, 100, 200, 500, 1000
  bool ordenOk = true;
  for (uint8_t i = 0; i < n; i++)
    if (movs[i].vaso != esperado[i] || movs[i].puestoDestino != (int8_t)i) ordenOk = false;
  comprobar(ordenOk, "orden ascendente por valor");

  for (uint8_t i = 0; i < n; i++) {                 // aplicar el plan
    vasos[movs[i].vaso].zona = movs[i].zonaDestino;
    vasos[movs[i].vaso].puesto = movs[i].puestoDestino;
  }
  comprobar(Planificador::planificar(vasos, POR_VALOR, 1, movs) == 0,
            "si ya esta ordenado no mueve nada");

  n = Planificador::planificar(vasos, POR_VALOR, -1, movs);
  bool usaHueco = false;
  for (uint8_t i = 0; i < n; i++) if (movs[i].liberar) usaHueco = true;
  comprobar(n > 0 && n <= 10 && usaHueco,
            "reordenar el rack lleno usa los huecos de la entrada");

  // --- secuenciador completo: se ejecuta el ciclo entero en el PC
  Vaso lote[N_PUESTOS] = {
      {500, 12, ZONA_ENTRADA, 0}, {100, 30, ZONA_ENTRADA, 1}, {1000, 8, ZONA_ENTRADA, 2},
      {50, 25, ZONA_ENTRADA, 3}, {200, 17, ZONA_ENTRADA, 4}};
  BusServos bus;
  bus.iniciar();
  Secuenciador sec;
  comprobar(sec.iniciar(lote, POR_VALOR, 1), "el secuenciador arranca el plan");

  float simulado = 0.0f;
  uint32_t vueltas = 0;
  while (sec.ocupado() && vueltas < 20000) {
    sec.actualizar(DT_CONTROL, bus);
    bus.actualizar(DT_CONTROL);
    simulado += DT_CONTROL;
    vueltas++;
  }
  comprobar(sec.estado() != Secuenciador::ERROR, "el ciclo termina sin errores");
  comprobar(simulado > 20.0f && simulado < 60.0f, "el ciclo dura lo previsto");

  bool rackOk = true;
  const uint16_t esperadoRack[5] = {50, 100, 200, 500, 1000};
  for (uint8_t i = 0; i < N_PUESTOS; i++) {
    bool encontrado = false;
    for (uint8_t j = 0; j < N_PUESTOS; j++)
      if (lote[j].zona == ZONA_RACK && lote[j].puesto == (int8_t)i &&
          lote[j].denominacion == esperadoRack[i]) encontrado = true;
    if (!encontrado) rackOk = false;
  }
  comprobar(rackOk, "el rack queda ordenado de $50 a $1000");

  Cinematica::fk(bus.pose(), x, y, z, phi);
  comprobar(cerca(x, 15.0f, 0.5f) && cerca(z, 19.0f, 0.5f), "el brazo vuelve al reposo");
  printf("  ciclo simulado: %.1f s en %u vueltas de control\n", (double)simulado, vueltas);

  printf(fallos == 0 ? "\nTodo en orden\n" : "\n%d prueba(s) fallaron\n", fallos);
  return fallos == 0 ? 0 : 1;
}
