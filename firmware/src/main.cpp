#include "pico/stdlib.h"

#include "FreeRTOS.h"
#include "task.h"

#include "tasks/SerialTask.hpp"

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

    xTaskCreate(serial_task, "serial", 1024, NULL, tskIDLE_PRIORITY + 1, NULL);
    vTaskStartScheduler();

    while (true) {
    }
}
