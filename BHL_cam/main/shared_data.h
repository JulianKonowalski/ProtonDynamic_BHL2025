#pragma once
#include "freertos/FreeRTOS.h"
#include <stdbool.h>
typedef struct
{
    float temperature;
    float humidity;
    bool water_level_ok;
    float heater_power;
    bool heater_on;
    bool sprinkler_on;
    bool leds_on;
    TickType_t last_update;
} system_data_t;

typedef struct
{
    float target_temperature;
    float target_humidity;
    bool sprinkler_enabled;
    bool leds_enabled;
    bool heater_enabled;
    float heater_power_limit;
    bool manual_mode; // true if manual mode is enabled
    int color;        // RGB color for LEDs
    TickType_t last_updated;
} app_settings_t;

extern system_data_t shared_data;
extern app_settings_t app_settings;

extern SemaphoreHandle_t data_mutex;
extern SemaphoreHandle_t settings_mutex;