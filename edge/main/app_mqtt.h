
#ifndef _APP_MQTT_H_
#define _APP_MQTT_H_

#ifdef __cplusplus
extern "C" {
#endif

void app_mqtt_main(QueueHandle_t queue, bool returnFB);
esp_err_t mqtt_handler();

#ifdef __cplusplus
}
#endif

#endif