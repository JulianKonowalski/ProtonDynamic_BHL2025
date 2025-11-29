#pragma once

#ifdef __cplusplus
extern "C"
{
#endif

    /**
     * @brief Inicjalizuje i uruchamia task do cyklicznego odczytu danych z czujnika DHT11.
     *
     * Odczytana temperatura i wilgotność są zapisywane do struktury shared_data
     * zabezpieczonej semaforem mutex (data_mutex).
     */
    void sensor_task(void *pvParameters);

#ifdef __cplusplus
}
#endif