#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/timer.h"

#include "FreeRTOS.h"
#include "task.h"

int64_t alarm_callback(alarm_id_t id, void *user_data) {
    // Put your timeout handler code in here
    return 0;
}

static void main_task(void *params)
{
    (void)params;

#if defined(PICO_DEFAULT_LED_PIN)
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
#endif

    add_alarm_in_ms(2000, alarm_callback, NULL, false);

    while (true) {
#if defined(PICO_DEFAULT_LED_PIN)
        gpio_put(PICO_DEFAULT_LED_PIN, 1);
#endif
        printf("Hello from FreeRTOS\n");
        vTaskDelay(pdMS_TO_TICKS(500));

#if defined(PICO_DEFAULT_LED_PIN)
        gpio_put(PICO_DEFAULT_LED_PIN, 0);
#endif
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

extern "C" void vApplicationTickHook(void)
{
}

extern "C" void vApplicationMallocFailedHook(void)
{
    taskDISABLE_INTERRUPTS();
    while (true) {
    }
}

extern "C" void vApplicationStackOverflowHook(TaskHandle_t task, char *task_name)
{
    (void)task;
    (void)task_name;

    taskDISABLE_INTERRUPTS();
    while (true) {
    }
}

int main()
{
    stdio_init_all();

    xTaskCreate(main_task, "main", 256, NULL, tskIDLE_PRIORITY + 1, NULL);
    vTaskStartScheduler();

    while (true) {
    }
}
