
#include "shared_data.h"
#include "esp_log.h"
#include "sensor_temp_humidity.h"
#include "dht.h"

#define DHT_GPIO 33

void sensor_task(void *pvParameters)
{
    while (1)
    {
        float temperature = 0, humidity = 0;
        esp_err_t res = dht_read_float_data(DHT_TYPE_DHT11, DHT_GPIO, &humidity, &temperature);

        if (res == ESP_OK)
        {
            if (xSemaphoreTake(data_mutex, pdMS_TO_TICKS(100)))
            {
                shared_data.temperature = temperature;
                shared_data.humidity = humidity;
                shared_data.last_update = xTaskGetTickCount();
                xSemaphoreGive(data_mutex);
            }
            ESP_LOGI("SENSOR", "T: %.1f °C  H: %.1f %%", temperature, humidity);
        }
        else
        {
            ESP_LOGW("SENSOR", "Błąd odczytu z DHT11: %d", res);
        }

        vTaskDelay(pdMS_TO_TICKS(3000)); // odczyt co 3 sekundy
    }
}