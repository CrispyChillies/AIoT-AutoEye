
#ifndef _APP_MODEL_H_
#define _APP_MODEL_H_

#include <cstdint>

#ifdef __cplusplus
extern "C" {
#endif

esp_err_t run_model(float* data, const uint32_t length);

#ifdef __cplusplus
}
#endif

#endif