/*
 * ============================================================================
 * CÓDIGO MÍNIMO — SOLO MOVER LOS 3 MOTORES PASO A PASO (+ 2 SERVOS EN 90°)
 * ============================================================================
 * Basado directamente en tu ejemplo funcional C:\Users\samue\CLionProjects\ESP\main.cpp
 *
 * Pines ESP32:
 *   Motor 1 (Base)   : STEP (CLK+) = 26, DIR (CW+) = 25
 *   Motor 2 (Hombro) : STEP (CLK+) = 33, DIR (CW+) = 32
 *   Motor 3 (Codo)   : STEP (CLK+) = 27, DIR (CW+) = 14
 *   Enable común     : EN+         = 13 (LOW = habilitado; opcional en TB6560/TB6600)
 *   Servo 1 (Pitch)  : PWM         = 18 (fijo en 90°)
 *   Servo 2 (Garra)  : PWM         = 19 (fijo en 90°)
 *
 * Comandos por Serial (115200 baud, Nueva línea):
 *   M1 <pos>   / M2 <pos>   / M3 <pos>   -> Posición absoluta en pasos (ej: M1 200)
 *   R1 <pasos> / R2 <pasos> / R3 <pasos> -> Mover pasos relativos (ej: R1 -100)
 *   SPEED <vel>                          -> Velocidad máxima en pasos/s (ej: SPEED 800)
 *   ZERO                                 -> Poner contador actual de M1, M2, M3 en 0
 *   STOP                                 -> Parar los 3 motores de inmediato
 *   EN <1|0>                             -> Habilitar (1) o deshabilitar (0)
 * ============================================================================
 */

#include <Arduino.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// Pines motores paso a paso
constexpr uint8_t M1_STEP_PIN = 26;
constexpr uint8_t M1_DIR_PIN  = 25;

constexpr uint8_t M2_STEP_PIN = 33;
constexpr uint8_t M2_DIR_PIN  = 32;

constexpr uint8_t M3_STEP_PIN = 27;
constexpr uint8_t M3_DIR_PIN  = 14;

constexpr uint8_t EN_PIN      = 13;

// Pines servos (fijos en 90°)
constexpr uint8_t SERVO1_PIN  = 18;
constexpr uint8_t SERVO2_PIN  = 19;

// Velocidad y aceleración por defecto (idénticas a tu main.cpp que funciona)
constexpr float DEFAULT_MAX_SPEED = 1200.0f; // pasos/s
constexpr float DEFAULT_ACCEL     = 2500.0f; // pasos/s^2
constexpr float MIN_START_SPEED   = 60.0f;   // pasos/s

class StepperAxis {
public:
  StepperAxis(uint8_t stepPin, uint8_t dirPin)
      : _stepPin(stepPin), _dirPin(dirPin) {}

  void begin() {
    pinMode(_stepPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    digitalWrite(_stepPin, LOW);
    digitalWrite(_dirPin, LOW);
    unsigned long now = micros();
    _lastVelUpdateMicros = now;
    _lastStepMicros = now;
  }

  void setEnabled(bool enabled) {
    _enabled = enabled;
    if (!enabled) {
      _speed = 0.0f;
      _targetPos = _currentPos;
    }
  }

  void setTarget(long target) { _targetPos = target; }
  void moveRelative(long delta) { _targetPos += delta; }
  long getCurrentPos() const { return _currentPos; }
  long getTargetPos() const { return _targetPos; }

  void setMaxSpeed(float maxSpeed) {
    if (maxSpeed >= 10.0f && maxSpeed <= 20000.0f) {
      _maxSpeed = maxSpeed;
    }
  }

  void stopNow() {
    _targetPos = _currentPos;
    _speed = 0.0f;
  }

  void zero() {
    _currentPos = 0;
    _targetPos = 0;
    _speed = 0.0f;
  }

  bool isMoving() const {
    return (_currentPos != _targetPos) || (fabsf(_speed) > 0.0f);
  }

  void update(unsigned long nowMicros) {
    if (!_enabled) {
      _lastVelUpdateMicros = nowMicros;
      return;
    }

    // 1. Rampa de velocidad cada 1 ms
    if ((unsigned long)(nowMicros - _lastVelUpdateMicros) >= 1000UL) {
      unsigned long elapsed = nowMicros - _lastVelUpdateMicros;
      if (elapsed > 20000UL) elapsed = 1000UL;
      float dt = elapsed * 1e-6f;
      _lastVelUpdateMicros = nowMicros;

      long dist = _targetPos - _currentPos;
      float stopDist = (_speed * _speed) / (2.0f * _accel);

      if (dist == 0) {
        if (stopDist < 1.0f || fabsf(_speed) <= _minSpeed) {
          _speed = 0.0f;
        } else {
          float decel = _accel * dt;
          if (fabsf(_speed) <= decel) {
            _speed = 0.0f;
          } else {
            _speed -= (_speed > 0.0f ? decel : -decel);
          }
        }
      } else {
        float dirToTarget = (dist > 0) ? 1.0f : -1.0f;
        if (_speed == 0.0f) {
          _speed = dirToTarget * _minSpeed;
        } else if ((_speed * dirToTarget) < 0.0f) {
          _speed += dirToTarget * _accel * dt;
        } else if ((float)labs(dist) <= stopDist) {
          float decel = _accel * dt;
          if (fabsf(_speed) - decel <= _minSpeed) {
            _speed = dirToTarget * _minSpeed;
          } else {
            _speed -= dirToTarget * decel;
          }
        } else {
          _speed += dirToTarget * _accel * dt;
          if (fabsf(_speed) > _maxSpeed) {
            _speed = dirToTarget * _maxSpeed;
          }
        }
      }
    }

    // 2. Pulso STEP/CLK
    if (fabsf(_speed) >= 1.0f) {
      unsigned long stepInterval = (unsigned long)(1000000.0f / fabsf(_speed));
      if ((unsigned long)(nowMicros - _lastStepMicros) >= stepInterval) {
        _lastStepMicros = nowMicros;

        int8_t dir = (_speed > 0.0f) ? 1 : -1;
        if (dir != _lastDir) {
          digitalWrite(_dirPin, dir > 0 ? HIGH : LOW);
          delayMicroseconds(20);
          _lastDir = dir;
        }

        digitalWrite(_stepPin, HIGH);
        delayMicroseconds(15);
        digitalWrite(_stepPin, LOW);

        _currentPos += dir;

        if (_currentPos == _targetPos && fabsf(_speed) <= _minSpeed) {
          _speed = 0.0f;
        }
      }
    }
  }

private:
  uint8_t _stepPin;
  uint8_t _dirPin;
  bool _enabled = true;
  int8_t _lastDir = 0;

  long _currentPos = 0;
  long _targetPos = 0;
  float _speed = 0.0f;
  float _maxSpeed = DEFAULT_MAX_SPEED;
  float _accel = DEFAULT_ACCEL;
  float _minSpeed = MIN_START_SPEED;

  unsigned long _lastVelUpdateMicros = 0;
  unsigned long _lastStepMicros = 0;
};

StepperAxis motor1(M1_STEP_PIN, M1_DIR_PIN);
StepperAxis motor2(M2_STEP_PIN, M2_DIR_PIN);
StepperAxis motor3(M3_STEP_PIN, M3_DIR_PIN);

static char cmdBuffer[128];
static size_t cmdLen = 0;

void setupServos90() {
  uint32_t duty90 = (uint32_t)((1500ULL * 65535ULL) / 20000ULL);
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  ledcAttach(SERVO1_PIN, 50, 16);
  ledcAttach(SERVO2_PIN, 50, 16);
  ledcWrite(SERVO1_PIN, duty90);
  ledcWrite(SERVO2_PIN, duty90);
#else
  ledcSetup(0, 50, 16);
  ledcSetup(1, 50, 16);
  ledcAttachPin(SERVO1_PIN, 0);
  ledcAttachPin(SERVO2_PIN, 1);
  ledcWrite(0, duty90);
  ledcWrite(1, duty90);
#endif
}

void processCommand(char* line) {
  while (*line == ' ' || *line == '\t') line++;
  if (*line == '\0') return;

  for (char* p = line; *p != '\0'; p++) {
    if (*p == ':') *p = ' ';
  }

  char* cmd = strtok(line, " \t");
  if (!cmd) return;
  for (char* p = cmd; *p; p++) *p = toupper((unsigned char)*p);

  char* arg = strtok(nullptr, " \t");

  if (strcmp(cmd, "M1") == 0 && arg) {
    motor1.setTarget(atol(arg));
  } else if (strcmp(cmd, "M2") == 0 && arg) {
    motor2.setTarget(atol(arg));
  } else if (strcmp(cmd, "M3") == 0 && arg) {
    motor3.setTarget(atol(arg));
  } else if (strcmp(cmd, "R1") == 0 && arg) {
    motor1.moveRelative(atol(arg));
  } else if (strcmp(cmd, "R2") == 0 && arg) {
    motor2.moveRelative(atol(arg));
  } else if (strcmp(cmd, "R3") == 0 && arg) {
    motor3.moveRelative(atol(arg));
  } else if (strcmp(cmd, "SPEED") == 0 && arg) {
    float s = atof(arg);
    motor1.setMaxSpeed(s);
    motor2.setMaxSpeed(s);
    motor3.setMaxSpeed(s);
  } else if (strcmp(cmd, "STOP") == 0) {
    motor1.stopNow();
    motor2.stopNow();
    motor3.stopNow();
  } else if (strcmp(cmd, "ZERO") == 0) {
    motor1.zero();
    motor2.zero();
    motor3.zero();
  } else if (strcmp(cmd, "EN") == 0 && arg) {
    bool en = (atoi(arg) != 0);
    digitalWrite(EN_PIN, en ? LOW : HIGH);
    motor1.setEnabled(en);
    motor2.setEnabled(en);
    motor3.setEnabled(en);
  }
}

void readSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\r' || c == '\n') {
      if (cmdLen > 0) {
        cmdBuffer[cmdLen] = '\0';
        processCommand(cmdBuffer);
        cmdLen = 0;
      }
    } else if (cmdLen < sizeof(cmdBuffer) - 1) {
      cmdBuffer[cmdLen++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW); // Habilitado

  motor1.begin();
  motor2.begin();
  motor3.begin();

  setupServos90();
  Serial.println("LISTO: M1/M2/M3 <pos>, R1/R2/R3 <pasos>, SPEED <vel>, ZERO, STOP");
}

void loop() {
  readSerial();

  unsigned long now = micros();
  motor1.update(now);
  motor2.update(now);
  motor3.update(now);
}
