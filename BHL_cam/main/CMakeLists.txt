idf_component_register(
    SRCS "shared_data.c" "main.c"
    "sensors/sensor_temp_humidity.c"
    INCLUDE_DIRS "." "sensors" 
    REQUIRES esp32-camera nvs_flash esp_wifi esp_netif esp_event dht
)