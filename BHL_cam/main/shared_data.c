#include "shared_data.h"

system_data_t shared_data = {0};
app_settings_t app_settings = {0};
SemaphoreHandle_t data_mutex = NULL;
SemaphoreHandle_t settings_mutex = NULL;