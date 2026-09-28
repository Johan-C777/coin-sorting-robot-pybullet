# Pruebas del núcleo del firmware compiladas en el PC.
#   make            compila y ejecuta
#   make limpiar    borra el binario
CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
FUENTES = test_core.cpp stub_servo_bus.cpp ../esp32_brazo/kinematics.cpp \
          ../esp32_brazo/trajectory.cpp ../esp32_brazo/planner.cpp \
          ../esp32_brazo/cups.cpp ../esp32_brazo/protocol.cpp ../esp32_brazo/sequencer.cpp

all: test_core
	./test_core

test_core: $(FUENTES)
	$(CXX) $(CXXFLAGS) -o $@ $(FUENTES) -lm

limpiar:
	rm -f test_core

.PHONY: all limpiar
