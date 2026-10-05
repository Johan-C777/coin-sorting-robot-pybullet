# Pruebas del núcleo de los dos firmwares, compiladas en el PC.
#   make            compila y ejecuta las dos
#   make limpiar    borra los binarios
CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

BRAZO = test_core.cpp stub_servo_bus.cpp ../esp32_brazo/kinematics.cpp \
        ../esp32_brazo/trajectory.cpp ../esp32_brazo/planner.cpp \
        ../esp32_brazo/cups.cpp ../esp32_brazo/protocol.cpp ../esp32_brazo/sequencer.cpp
CONTADOR = test_conteo.cpp ../esp32_contador/conteo.cpp

all: test_core test_conteo
	./test_core
	./test_conteo

test_core: $(BRAZO)
	$(CXX) $(CXXFLAGS) -o $@ $(BRAZO) -lm

test_conteo: $(CONTADOR)
	$(CXX) $(CXXFLAGS) -o $@ $(CONTADOR)

limpiar:
	rm -f test_core test_conteo

.PHONY: all limpiar
