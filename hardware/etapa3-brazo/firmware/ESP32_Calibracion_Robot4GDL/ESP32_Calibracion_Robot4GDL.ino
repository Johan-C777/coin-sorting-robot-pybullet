/*
 * ============================================================================
 * ROBOT 4 GDL + GARRA (EEZYbotARM 40cm NEMA 17 + Planetaria + 2x SG90)
 * FASE 1: Calibración de Cero (0) y Límites en Pasos vía USB SERIAL (115200)
 * ============================================================================
 * Arquitectura sin latencia (idéntica a C:\Users\samue\CLionProjects\ESP\main.cpp):
 *   - Comandos de movimiento no bloqueantes (respuesta instantánea)
 *   - Telemetría push automática cada 100 ms mientras se mueven (y al detenerse)
 *   - Rampa StepperAxis cada 1 ms, pulso CLK=20 us, setup CW=25 us (TB6560/TB6600)
 *   - Buffer Serial TX/RX de 2048 bytes, cero asignaciones String en loop()
 *
 * Pines ESP32 (DevKit 30 y 38 pines):
 *   - J1 (Base / Torreta)      : STEP (CLK+) = 26, DIR (CW+) = 25
 *   - J2 (Hombro / Brazo 004)  : STEP (CLK+) = 33, DIR (CW+) = 32
 *   - J3 (Codo / Palanca 002)  : STEP (CLK+) = 27, DIR (CW+) = 14
 *   - Enable común (opcional)  : EN+         = 13 (activo LOW; desconectable en TB6560/TB6600)
 *   - Servo J4 (Muñeca Pitch)  : PWM         = 18 (FIJO EN 90°)
 *   - Servo Garra (Pinza)      : PWM         = 19 (FIJO EN 90°)
 * ============================================================================
 */

#include <Arduino.h>
#include <Preferences.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// 1. ASIGNACIÓN DE PINES ESP32
// ============================================================================
constexpr uint8_t J1_STEP_PIN        = 26;
constexpr uint8_t J1_DIR_PIN         = 25;

constexpr uint8_t J2_STEP_PIN        = 33;
constexpr uint8_t J2_DIR_PIN         = 32;

constexpr uint8_t J3_STEP_PIN        = 27;
constexpr uint8_t J3_DIR_PIN         = 14;

constexpr uint8_t STEPPERS_EN_PIN    = 13;

constexpr uint8_t SERVO_J4_PITCH_PIN = 18;
constexpr uint8_t SERVO_GARRA_PIN    = 19;

constexpr uint32_t SERVO_FREQ_HZ   = 50;
constexpr uint8_t  SERVO_RES_BITS  = 16;
constexpr int      SERVO_MIN_US    = 500;
constexpr int      SERVO_MAX_US    = 2500;
constexpr int      SERVO_FIXED_DEG = 90;

// Parámetros probados para TB6560/TB6600 + 24V (como en main.cpp)
constexpr float DEFAULT_MAX_SPEED  = 800.0f;  // pasos/segundo
constexpr float DEFAULT_ACCEL      = 2500.0f; // pasos/segundo^2
constexpr float MIN_START_SPEED    = 80.0f;   // pasos/segundo

// ============================================================================
// 2. CLASE StepperAxis (basada en main.cpp, corregido overshoot en destino)
// ============================================================================
class StepperAxis {
public:
  const char* id;
  bool invertDir = false;
  bool zeroSet   = false;
  bool minSet    = false;
  long minSteps  = 0;
  bool maxSet    = false;
  long maxSteps  = 0;

  StepperAxis(const char* axisId, uint8_t stepPin, uint8_t dirPin)
      : id(axisId), _stepPin(stepPin), _dirPin(dirPin) {}

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

  void setInvertDir(bool inv) {
    invertDir = inv;
    _lastDir = 0;
  }

  void setTarget(long target) { _targetPos = target; }
  void moveRelative(long delta) { _targetPos += delta; }
  long getCurrentPos() const { return _currentPos; }
  long getTargetPos() const { return _targetPos; }

  void setMaxSpeed(float maxSpeed) {
    _maxSpeed = constrain(maxSpeed, 20.0f, 10000.0f);
  }
  float getMaxSpeed() const { return _maxSpeed; }

  void stopNow() {
    _targetPos = _currentPos;
    _speed = 0.0f;
  }

  void zero() {
    _currentPos = 0;
    _targetPos = 0;
    _speed = 0.0f;
    zeroSet = true;
    minSet = false;
    minSteps = 0;
    maxSet = false;
    maxSteps = 0;
  }

  bool isMoving() const {
    return (_currentPos != _targetPos);
  }

  void update(unsigned long nowMicros) {
    if (!_enabled) {
      _lastVelUpdateMicros = nowMicros;
      return;
    }

    long dist = _targetPos - _currentPos;
    if (dist == 0) {
      _speed = 0.0f;
      _lastVelUpdateMicros = nowMicros;
      return;
    }

    float effMin = min(_minSpeed, _maxSpeed);
    float dirToTarget = (dist > 0) ? 1.0f : -1.0f;

    // Arranque inmediato sin esperar 1 ms cuando viene desde reposo
    if (_speed == 0.0f) {
      _speed = dirToTarget * effMin;
      _lastVelUpdateMicros = nowMicros;
      _lastStepMicros = nowMicros - (unsigned long)(1000000.0f / effMin);
    }

    // 1. Actualizar rampa de velocidad cada 1 ms
    if ((unsigned long)(nowMicros - _lastVelUpdateMicros) >= 1000UL) {
      unsigned long elapsed = nowMicros - _lastVelUpdateMicros;
      if (elapsed > 20000UL) elapsed = 1000UL;
      float dt = elapsed * 1e-6f;
      _lastVelUpdateMicros = nowMicros;

      float stopDist = (_speed * _speed) / (2.0f * _accel);

      if ((_speed * dirToTarget) < 0.0f) {
        // Cambio de sentido: frenar y revertir
        _speed += dirToTarget * _accel * dt;
        if (fabsf(_speed) < effMin) _speed = dirToTarget * effMin;
      } else if ((float)labs(dist) <= stopDist) {
        // Frenado suave hacia el objetivo
        float decel = _accel * dt;
        if (fabsf(_speed) - decel <= effMin) {
          _speed = dirToTarget * effMin;
        } else {
          _speed -= dirToTarget * decel;
        }
      } else {
        // Aceleración hacia _maxSpeed
        _speed += dirToTarget * _accel * dt;
        if (fabsf(_speed) > _maxSpeed) {
          _speed = dirToTarget * _maxSpeed;
        }
      }
    }

    // 2. Generar pulso STEP/CLK cuando se cumpla el intervalo
    if (fabsf(_speed) >= 1.0f) {
      unsigned long stepInterval = (unsigned long)(1000000.0f / fabsf(_speed));
      if ((unsigned long)(nowMicros - _lastStepMicros) >= stepInterval) {
        _lastStepMicros = nowMicros;

        int8_t dir = (_speed > 0.0f) ? 1 : -1;
        if (dir != _lastDir) {
          bool level = (dir > 0) ? HIGH : LOW;
          if (invertDir) level = !level;
          digitalWrite(_dirPin, level);
          delayMicroseconds(25); // Setup CW/DIR para optoacopladores 4N35/6N137
          _lastDir = dir;
        }

        digitalWrite(_stepPin, HIGH);
        delayMicroseconds(20); // Pulso CLK/STEP amplio para TB6560/TB6600
        digitalWrite(_stepPin, LOW);

        _currentPos += dir;

        if (_currentPos == _targetPos) {
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

StepperAxis motors[3] = {
  StepperAxis("J1_base",   J1_STEP_PIN, J1_DIR_PIN),
  StepperAxis("J2_hombro", J2_STEP_PIN, J2_DIR_PIN),
  StepperAxis("J3_codo",   J3_STEP_PIN, J3_DIR_PIN)
};

bool steppersEnabled = true;
float globalMaxSpeed = DEFAULT_MAX_SPEED;
String savedUiMetaJson = "{}";

static char rxBuf[3800];
static size_t rxLen = 0;
static char txBuf[640];
static unsigned long lastPushMs = 0;
static bool wasMovingAny = false;

Preferences prefs;

// ============================================================================
// 3. SERVOS SG90 FIJOS EN 90°
// ============================================================================
uint32_t degToDuty16(int deg) {
  deg = constrain(deg, 0, 180);
  uint32_t pulseUs = map(deg, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  return (uint32_t)(((uint64_t)pulseUs * 65535ULL) / 20000ULL);
}

void setupServosFixed90() {
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  ledcAttach(SERVO_J4_PITCH_PIN, SERVO_FREQ_HZ, SERVO_RES_BITS);
  ledcAttach(SERVO_GARRA_PIN,    SERVO_FREQ_HZ, SERVO_RES_BITS);
  ledcWrite(SERVO_J4_PITCH_PIN, degToDuty16(SERVO_FIXED_DEG));
  ledcWrite(SERVO_GARRA_PIN,    degToDuty16(SERVO_FIXED_DEG));
#else
  ledcSetup(0, SERVO_FREQ_HZ, SERVO_RES_BITS);
  ledcSetup(1, SERVO_FREQ_HZ, SERVO_RES_BITS);
  ledcAttachPin(SERVO_J4_PITCH_PIN, 0);
  ledcAttachPin(SERVO_GARRA_PIN,    1);
  ledcWrite(0, degToDuty16(SERVO_FIXED_DEG));
  ledcWrite(1, degToDuty16(SERVO_FIXED_DEG));
#endif
}

void writeServosFixed90() {
  uint32_t duty90 = degToDuty16(SERVO_FIXED_DEG);
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  ledcWrite(SERVO_J4_PITCH_PIN, duty90);
  ledcWrite(SERVO_GARRA_PIN,    duty90);
#else
  ledcWrite(0, duty90);
  ledcWrite(1, duty90);
#endif
}

void applySteppersEnable(bool enable) {
  steppersEnabled = enable;
  digitalWrite(STEPPERS_EN_PIN, enable ? LOW : HIGH);
  for (int i = 0; i < 3; i++) {
    motors[i].setEnabled(enable);
  }
}

void applyGlobalSpeed(float sp) {
  globalMaxSpeed = constrain(sp, 20.0f, 5000.0f);
  for (int i = 0; i < 3; i++) {
    motors[i].setMaxSpeed(globalMaxSpeed);
  }
}

// ============================================================================
// 4. PERSISTENCIA EN MEMORIA FLASH (NVS)
// ============================================================================
void saveCalibrationToNVS() {
  prefs.begin("robot_cal", false);
  prefs.putFloat("spd2", globalMaxSpeed);
  for (int i = 0; i < 3; i++) {
    char key[16];
    snprintf(key, sizeof(key), "m%d_inv",  i); prefs.putBool(key, motors[i].invertDir);
    snprintf(key, sizeof(key), "m%d_zset", i); prefs.putBool(key, motors[i].zeroSet);
    snprintf(key, sizeof(key), "m%d_minS", i); prefs.putBool(key, motors[i].minSet);
    snprintf(key, sizeof(key), "m%d_minV", i); prefs.putLong(key, motors[i].minSteps);
    snprintf(key, sizeof(key), "m%d_maxS", i); prefs.putBool(key, motors[i].maxSet);
    snprintf(key, sizeof(key), "m%d_maxV", i); prefs.putLong(key, motors[i].maxSteps);
  }
  prefs.putString("ui_meta", savedUiMetaJson);
  prefs.end();
}

void loadCalibrationFromNVS() {
  prefs.begin("robot_cal", true);
  applyGlobalSpeed(prefs.getFloat("spd2", DEFAULT_MAX_SPEED));
  for (int i = 0; i < 3; i++) {
    char key[16];
    snprintf(key, sizeof(key), "m%d_inv",  i); motors[i].setInvertDir(prefs.getBool(key, false));
    snprintf(key, sizeof(key), "m%d_zset", i); motors[i].zeroSet  = prefs.getBool(key, false);
    snprintf(key, sizeof(key), "m%d_minS", i); motors[i].minSet   = prefs.getBool(key, false);
    snprintf(key, sizeof(key), "m%d_minV", i); motors[i].minSteps = prefs.getLong(key, 0);
    snprintf(key, sizeof(key), "m%d_maxS", i); motors[i].maxSet   = prefs.getBool(key, false);
    snprintf(key, sizeof(key), "m%d_maxV", i); motors[i].maxSteps = prefs.getLong(key, 0);
  }
  savedUiMetaJson = prefs.getString("ui_meta", "{}");
  if (savedUiMetaJson.length() < 2 || !savedUiMetaJson.startsWith("{")) {
    savedUiMetaJson = "{}";
  }
  prefs.end();
}

// ============================================================================
// 5. TELEMETRÍA PUSH + COMANDOS INSTANTÁNEOS
// ============================================================================
void sendStatusJson() {
  int n = snprintf(
    txBuf, sizeof(txBuf),
    "{\"type\":\"status\",\"ok\":true,\"enabled\":%s,\"speed\":%.1f,\"servoPitchDeg\":%d,\"servoGarraDeg\":%d,\"motors\":[",
    steppersEnabled ? "true" : "false",
    globalMaxSpeed,
    SERVO_FIXED_DEG,
    SERVO_FIXED_DEG
  );

  for (int i = 0; i < 3; i++) {
    StepperAxis& m = motors[i];
    n += snprintf(
      txBuf + n, sizeof(txBuf) - n,
      "%s{\"id\":\"%s\",\"currentSteps\":%ld,\"targetSteps\":%ld,\"moving\":%s,"
      "\"invertDir\":%s,\"zeroSet\":%s,\"minSet\":%s,\"minSteps\":%ld,\"maxSet\":%s,\"maxSteps\":%ld}",
      (i > 0) ? "," : "",
      m.id,
      m.getCurrentPos(),
      m.getTargetPos(),
      m.isMoving() ? "true" : "false",
      m.invertDir ? "true" : "false",
      m.zeroSet ? "true" : "false",
      m.minSet ? "true" : "false",
      m.minSteps,
      m.maxSet ? "true" : "false",
      m.maxSteps
    );
  }
  snprintf(txBuf + n, sizeof(txBuf) - n, "]}");
  Serial.println(txBuf);
}

void processSerialLine(char* line) {
  while (*line == ' ' || *line == '\t') line++;
  if (*line == '\0') return;

  if (strcmp(line, "STATUS") == 0 || strcmp(line, "PING") == 0) {
    sendStatusJson();
    return;
  }

  if (strcmp(line, "GET_META") == 0) {
    Serial.print("{\"type\":\"meta\",\"ok\":true,\"uiMeta\":");
    Serial.print(savedUiMetaJson);
    Serial.println("}");
    return;
  }

  if (strcmp(line, "STOP") == 0) {
    for (int i = 0; i < 3; i++) motors[i].stopNow();
    sendStatusJson();
    return;
  }

  if (strcmp(line, "SERVOS_CENTER") == 0) {
    writeServosFixed90();
    sendStatusJson();
    return;
  }

  if (strcmp(line, "HOME_ALL") == 0) {
    if (!steppersEnabled) {
      Serial.println("{\"type\":\"err\",\"error\":\"Motores deshabilitados (Enable OFF)\"}");
      return;
    }
    for (int i = 0; i < 3; i++) {
      if (motors[i].zeroSet) motors[i].setTarget(0);
    }
    sendStatusJson();
    return;
  }

  if (strncmp(line, "SAVE_NVS ", 9) == 0) {
    char* payload = line + 9;
    while (*payload == ' ') payload++;
    size_t len = strlen(payload);
    if (len >= 2 && len < 3500 && payload[0] == '{') {
      savedUiMetaJson = String(payload);
    }
    saveCalibrationToNVS();
    sendStatusJson();
    return;
  }

  char* cmd  = strtok(line, " \t");
  char* arg1 = strtok(nullptr, " \t");
  char* arg2 = strtok(nullptr, " \t");
  if (!cmd) return;

  if (strcmp(cmd, "ENABLE") == 0 && arg1) {
    applySteppersEnable(atoi(arg1) != 0);
    sendStatusJson();
    return;
  }

  if (strcmp(cmd, "SPEED") == 0 && arg1) {
    applyGlobalSpeed(atof(arg1));
    sendStatusJson();
    return;
  }

  if (!arg1) return;
  int idx = atoi(arg1);
  if (idx < 0 || idx > 2) return;

  if (strcmp(cmd, "MOVE") == 0 && arg2) {
    if (!steppersEnabled) {
      Serial.println("{\"type\":\"err\",\"error\":\"Motores deshabilitados (Enable OFF)\"}");
      return;
    }
    motors[idx].moveRelative(atol(arg2));
    // No imprimimos JSON aquí para no retrasar el primer paso: el push de 100 ms actualiza el estado!
    return;
  }

  if (strcmp(cmd, "GOTO") == 0 && arg2) {
    if (!steppersEnabled) {
      Serial.println("{\"type\":\"err\",\"error\":\"Motores deshabilitados (Enable OFF)\"}");
      return;
    }
    motors[idx].setTarget(atol(arg2));
    return;
  }

  if (strcmp(cmd, "ZERO") == 0) {
    motors[idx].zero();
    saveCalibrationToNVS();
    sendStatusJson();
    return;
  }

  if (strcmp(cmd, "LIMIT") == 0 && arg2) {
    if (!motors[idx].zeroSet) {
      Serial.println("{\"type\":\"err\",\"error\":\"Fija primero el CERO (0) de este motor\"}");
      return;
    }
    long cur = motors[idx].getCurrentPos();
    if (strcasecmp(arg2, "MIN") == 0) {
      if (cur > 0) {
        Serial.println("{\"type\":\"err\",\"error\":\"El limite negativo debe ser <= 0\"}");
        return;
      }
      motors[idx].minSteps = cur;
      motors[idx].minSet = true;
    } else if (strcasecmp(arg2, "MAX") == 0) {
      if (cur < 0) {
        Serial.println("{\"type\":\"err\",\"error\":\"El limite positivo debe ser >= 0\"}");
        return;
      }
      motors[idx].maxSteps = cur;
      motors[idx].maxSet = true;
    }
    saveCalibrationToNVS();
    sendStatusJson();
    return;
  }

  if (strcmp(cmd, "CLEAR_LIMITS") == 0) {
    motors[idx].minSet = false;
    motors[idx].minSteps = 0;
    motors[idx].maxSet = false;
    motors[idx].maxSteps = 0;
    saveCalibrationToNVS();
    sendStatusJson();
    return;
  }

  if (strcmp(cmd, "INVERT") == 0 && arg2) {
    motors[idx].setInvertDir(atoi(arg2) != 0);
    saveCalibrationToNVS();
    sendStatusJson();
    return;
  }
}

void pollSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxLen > 0) {
        rxBuf[rxLen] = '\0';
        processSerialLine(rxBuf);
        rxLen = 0;
      }
    } else if (rxLen < sizeof(rxBuf) - 1) {
      rxBuf[rxLen++] = c;
    }
  }
}

// ============================================================================
// 6. SETUP Y LOOP PRINCIPAL
// ============================================================================
void setup() {
  Serial.setTxBufferSize(2048);
  Serial.setRxBufferSize(2048);
  Serial.begin(115200);
  delay(150);

  pinMode(STEPPERS_EN_PIN, OUTPUT);
  for (int i = 0; i < 3; i++) {
    motors[i].begin();
  }
  applySteppersEnable(true);

  setupServosFixed90();
  loadCalibrationFromNVS();
  sendStatusJson();
}

void loop() {
  pollSerial();

  unsigned long now = micros();
  motors[0].update(now);
  motors[1].update(now);
  motors[2].update(now);

  // Telemetría push idéntica a main.cpp: solo mientras se mueven (cada 100 ms) y al terminar
  bool movingAny = motors[0].isMoving() || motors[1].isMoving() || motors[2].isMoving();
  unsigned long nowMs = millis();
  if (movingAny && (nowMs - lastPushMs >= 100UL)) {
    lastPushMs = nowMs;
    sendStatusJson();
  } else if (!movingAny && wasMovingAny) {
    lastPushMs = nowMs;
    sendStatusJson();
  }
  wasMovingAny = movingAny;
}
