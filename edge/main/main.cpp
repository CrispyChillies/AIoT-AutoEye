#include "esp_camera.h"

#include <esp_log.h>
#include <esp_system.h>
#include <nvs_flash.h>
#include "esp_event.h"
#include "esp_netif.h"

#include <sys/param.h>
#include <string.h>

#include "app_wifi.h"
#include "app_mqtt.h"
#include "app_model.h"
#include "stream_server.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#ifndef portTICK_RATE_MS
#define portTICK_RATE_MS portTICK_PERIOD_MS
#endif

#define CAM_PIN_PWDN    -1 //power down is not used
#define CAM_PIN_RESET   -1 //software reset will be performed
#define CAM_PIN_XCLK    15
#define CAM_PIN_SIOD    4
#define CAM_PIN_SIOC    5

#define CAM_PIN_D7      16
#define CAM_PIN_D6      17
#define CAM_PIN_D5      18
#define CAM_PIN_D4      12
#define CAM_PIN_D3      10
#define CAM_PIN_D2      8
#define CAM_PIN_D1       9
#define CAM_PIN_D0       11
#define CAM_PIN_VSYNC   6
#define CAM_PIN_HREF    7
#define CAM_PIN_PCLK    13

static const char *TAG = "AIoT: AutoEye";

static esp_err_t init_camera(void) {

    static camera_config_t camera_config = {};

    camera_config.pin_pwdn  = CAM_PIN_PWDN;
    camera_config.pin_reset = CAM_PIN_RESET;
    camera_config.pin_xclk = CAM_PIN_XCLK;
    camera_config.pin_sccb_sda = CAM_PIN_SIOD;
    camera_config.pin_sccb_scl = CAM_PIN_SIOC;

    camera_config.pin_d7 = CAM_PIN_D7;
    camera_config.pin_d6 = CAM_PIN_D6;
    camera_config.pin_d5 = CAM_PIN_D5;
    camera_config.pin_d4 = CAM_PIN_D4;
    camera_config.pin_d3 = CAM_PIN_D3;
    camera_config.pin_d2 = CAM_PIN_D2;
    camera_config.pin_d1 = CAM_PIN_D1;
    camera_config.pin_d0 = CAM_PIN_D0;
    camera_config.pin_vsync = CAM_PIN_VSYNC;
    camera_config.pin_href = CAM_PIN_HREF;
    camera_config.pin_pclk = CAM_PIN_PCLK;

    camera_config.xclk_freq_hz = 20000000;
    camera_config.ledc_timer = LEDC_TIMER_0;
    camera_config.ledc_channel = LEDC_CHANNEL_0;

    camera_config.pixel_format = PIXFORMAT_GRAYSCALE;//YUV422,GRAYSCALE,RGB565,JPEG
    camera_config.frame_size = FRAMESIZE_96X96;//QQVGA-UXGA, For ESP32, do not use sizes above QVGA when not JPEG. The performance of the ESP32-S series has improved a lot, but JPEG mode always gives better frame rates.

    camera_config.jpeg_quality = 10; //0-63, for OV series camera sensors, lower number means higher quality
    camera_config.fb_count = 2; //When jpeg mode is used, if fb_count more than one, the driver will work in continuous mode.
    camera_config.grab_mode = CAMERA_GRAB_LATEST; //CAMERA_GRAB_LATEST. Sets when buffers should be filled
    camera_config.fb_location = CAMERA_FB_IN_PSRAM;

    //initialize the camera
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK)
    {
        ESP_LOGE(TAG, "Camera Init Failed");
        return err;
    }

    return ESP_OK;
}

static QueueHandle_t xQueueIFrame = NULL;

extern "C" void app_main(void) {

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    app_wifi_main();

    if(ESP_OK != init_camera()) {
        return;
    }
    xQueueIFrame = xQueueCreate(2, sizeof(camera_fb_t *));
    app_mqtt_main(xQueueIFrame, true);
    start_stream_server(xQueueIFrame, true);

    while (1) {
        ESP_LOGI(TAG, "Taking picture...");
        camera_fb_t *pic = esp_camera_fb_get();

        // use pic->buf to access the image
        if (pic) {
            xQueueSend(xQueueIFrame, &pic, portMAX_DELAY);
        }
        run_model(pic->buf, pic->len);
        mqtt_handler();
        vTaskDelay(700 / portTICK_RATE_MS);
    }
}