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

  // --- cinemática inversa: ejemplo de la memoria de cálculo (24° y 6,8 cm)
  float px, py;
  Cinematica::posePuesto(24.0f, 6.8f, px, py);
  ResultadoIK r = Cinematica::ik(px, py, 6.8f);
  comprobar(r.ok, "ik del ejemplo resuelto tiene solucion");
  comprobar(cerca(r.q[0], 24.00f, 0.01f) && cerca(r.q[1], 49.02f, 0.01f) &&
            cerca(r.q[2], -82.53f, 0.01f) && cerca(r.q[3], -56.50f, 0.01f),
            "ik del ejemplo coincide con la memoria de calculo");
  Cinematica::posePuesto(YAW_RACK[0], Z_AGARRE, px, py);
  ResultadoIK r1 = Cinematica::ik(px, py, Z_AGARRE);
  comprobar(r1.ok && cerca(r1.q[0], 12.00f, 0.01f) && cerca(r1.q[1], 44.75f, 0.01f) &&
            cerca(r1.q[2], -83.87f, 0.01f) && cerca(r1.q[3], -50.88f, 0.01f),
            "ik del puesto R1 (12 grados, 4,8 cm)");

  // --- ida y vuelta en los dieciocho puestos
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
  comprobar(idaYVuelta, "los dieciocho puestos resuelven ida y vuelta a las dos alturas");

  // --- fuera del alcance y fuera de limite
  comprobar(!Cinematica::ik(40.0f, 30.0f, Z_AGARRE).ok, "punto lejano se rechaza");
  ResultadoIK lim = Cinematica::ik(2.0f, 0.0f, 2.0f);
  comprobar(!lim.ok, "pose imposible se rechaza antes de mover");

  // --- trama de servos
  char buf[32];
  Protocolo::armarTrama(Q_HOME, PINZA_ABIERTA_MM, buf, sizeof(buf));
  comprobar(strcmp(buf, "S:90,90,90,30,90,85") == 0, "trama de reposo");
  Protocolo::armarTrama(r.q, PINZA_ABIERTA_MM, buf, sizeof(buf));
  comprobar(strcmp(buf, "S:114,49,83,64,90,85") == 0, "trama del ejemplo resuelto");
  comprobar(Protocolo::microsegundos(114) == 1767 && Protocolo::microsegundos(90) == 1500,
            "anchos de pulso");
  int16_t leidos[N_CANALES];
  comprobar(Protocolo::leerTrama("S:114,49,83,64,90,85", leidos) && leidos[0] == 114 &&
            leidos[5] == 85, "lectura de trama");
  comprobar(!Protocolo::leerTrama("X:1,2,3", leidos), "trama invalida se rechaza");

  // --- lote del contador con monedas antiguas y nuevas
  Vaso leido[N_PUESTOS] = {};
  const uint8_t nv = Protocolo::leerVasos("VASOS:500x12a12,100x30,1000x8,50x25,200x17,100x10a10,50x9a9,500x8,200x6a6", leido);
  comprobar(nv == 9 && leido[1].denominacion == 100 && leido[1].monedas == 30 &&
            leido[5].antiguas == 10 && leido[1].antiguas == 0 && leido[8].puesto == 8,
            "lectura del lote VASOS con antiguas");
  comprobar(Protocolo::leerVasos("VASOS:500x12a20", leido) == 0 &&
            Protocolo::leerVasos("VASOS:abc", leido) == 0 &&
            Protocolo::leerVasos("S:1,2,3", leido) == 0, "lote invalido se rechaza");
  comprobar(Protocolo::leerVasos("VASOS:50x24,100x20,200x18,500x14,1000x12,50x4,100x4,200x4,500x4", leido) == 9 &&
            leido[2].antiguas == 0, "la trama sin antiguas sigue siendo valida");
  const Vaso mezcla = {100, 30, ZONA_ENTRADA, 0, 10};
  comprobar(cerca(Vasos::pesoG(mezcla), 137.9f, 0.05f) && Vasos::valor(mezcla) == 3000u,
            "peso con 20 nuevas y 10 antiguas de $100");
  comprobar(Protocolo::criterioDeTexto("antiguas") == POR_ANTIGUAS &&
            Protocolo::criterioDeTexto("peso") == POR_PESO &&
            Protocolo::criterioDeTexto("otro") == POR_VALOR, "criterios de orden por nombre");

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
      {500, 12, ZONA_ENTRADA, 0, 12}, {100, 30, ZONA_ENTRADA, 1, 0}, {1000, 8, ZONA_ENTRADA, 2, 0},
      {50, 25, ZONA_ENTRADA, 3, 0}, {200, 17, ZONA_ENTRADA, 4, 0}, {100, 10, ZONA_ENTRADA, 5, 10},
      {50, 9, ZONA_ENTRADA, 6, 9}, {500, 8, ZONA_ENTRADA, 7, 0}, {200, 6, ZONA_ENTRADA, 8, 6}};
  Movimiento movs[2 * N_PUESTOS];
  uint8_t n = Planificador::planificar(vasos, POR_VALOR, 1, movs);
  comprobar(n == 9, "desde la entrada son nueve movimientos");
  const uint8_t esperado[9] = {6, 5, 8, 3, 1, 4, 7, 0, 2};   // por valor total del vaso
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
  comprobar(n > 0 && n <= 2 * N_PUESTOS && usaHueco,
            "reordenar el rack lleno usa los huecos de la entrada");

  // --- por peso, las monedas antiguas cambian el orden
  Vaso porPeso[N_PUESTOS] = {
      {500, 12, ZONA_ENTRADA, 0, 12}, {100, 30, ZONA_ENTRADA, 1, 0}, {1000, 8, ZONA_ENTRADA, 2, 0},
      {50, 25, ZONA_ENTRADA, 3, 0}, {200, 17, ZONA_ENTRADA, 4, 0}, {100, 10, ZONA_ENTRADA, 5, 10},
      {50, 9, ZONA_ENTRADA, 6, 9}, {500, 8, ZONA_ENTRADA, 7, 0}, {200, 6, ZONA_ENTRADA, 8, 6}};
  n = Planificador::planificar(porPeso, POR_PESO, 1, movs);
  const uint8_t esperadoPeso[9] = {6, 8, 3, 5, 7, 4, 2, 0, 1};   // de 58,5 g a 118,2 g
  bool pesoOk = (n == 9);
  for (uint8_t i = 0; i < n && pesoOk; i++)
    if (movs[i].vaso != esperadoPeso[i]) pesoOk = false;
  comprobar(pesoOk, "orden por peso con monedas antiguas");

  // --- secuenciador completo: se ejecuta el ciclo entero en el PC
  Vaso lote[N_PUESTOS] = {
      {500, 12, ZONA_ENTRADA, 0, 12}, {100, 30, ZONA_ENTRADA, 1, 0}, {1000, 8, ZONA_ENTRADA, 2, 0},
      {50, 25, ZONA_ENTRADA, 3, 0}, {200, 17, ZONA_ENTRADA, 4, 0}, {100, 10, ZONA_ENTRADA, 5, 10},
      {50, 9, ZONA_ENTRADA, 6, 9}, {500, 8, ZONA_ENTRADA, 7, 0}, {200, 6, ZONA_ENTRADA, 8, 6}};
  BusServos bus;
  bus.iniciar();
  Secuenciador sec;
  comprobar(sec.iniciar(lote, POR_VALOR, 1), "el secuenciador arranca el plan");

  float simulado = 0.0f;
  uint32_t vueltas = 0;
  while (sec.ocupado() && vueltas < 40000) {
    sec.actualizar(DT_CONTROL, bus);
    bus.actualizar(DT_CONTROL);
    simulado += DT_CONTROL;
    vueltas++;
  }
  comprobar(sec.estado() != Secuenciador::ERROR, "el ciclo termina sin errores");
  comprobar(simulado > 35.0f && simulado < 110.0f, "el ciclo dura lo previsto");

  bool rackOk = true;
  const uint8_t esperadoRack[9] = {6, 5, 8, 3, 1, 4, 7, 0, 2};
  for (uint8_t i = 0; i < N_PUESTOS; i++)
    if (lote[esperadoRack[i]].zona != ZONA_RACK || lote[esperadoRack[i]].puesto != (int8_t)i)
      rackOk = false;
  comprobar(rackOk, "el rack queda ordenado por valor de menor a mayor");

  Cinematica::fk(bus.pose(), x, y, z, phi);
  comprobar(cerca(x, 15.0f, 0.5f) && cerca(z, 19.0f, 0.5f), "el brazo vuelve al reposo");
  printf("  ciclo simulado: %.1f s en %u vueltas de control\n", (double)simulado, vueltas);

  printf(fallos == 0 ? "\nTodo en orden\n" : "\n%d prueba(s) fallaron\n", fallos);
  return fallos == 0 ? 0 : 1;
}
