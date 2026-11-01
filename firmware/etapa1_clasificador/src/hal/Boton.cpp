#include "Boton.h"

#include <soc/gpio_reg.h>
#include <soc/soc.h>

namespace hal {

void IRAM_ATTR Boton::isr(void *arg) {
  Boton *b = static_cast<Boton *>(arg);
  const uint32_t t = (uint32_t)esp_timer_get_time();
  if (t - b->ultimo_us_ < ANTIRREBOTE_US) return;
  b->ultimo_us_ = t;
  if (!((REG_READ(GPIO_IN_REG) >> PIN_BOTON) & 1)) {   // lectura de registro: segura en IRAM
    b->bajada_us_ = t;
    b->soltado_ = false;
  } else if (b->bajada_us_) {
    b->soltado_ = true;
  }
}

}  // namespace hal
