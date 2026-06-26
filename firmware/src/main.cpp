#include "pico/stdlib.h"

#include "FreeRTOS.h"
#include "queue.h"
#include "task.h"

#include "protocol/Command.hpp"
#include "tasks/MachineTask.hpp"
#include "tasks/SerialTask.hpp"

namespace {

constexpr UBaseType_t kCommandQueueDepth = 16;

} // namespace

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

    QueueHandle_t command_queue =
        xQueueCreate(kCommandQueueDepth, sizeof(Command));
    configASSERT(command_queue != nullptr);

    xTaskCreate(
        machine_task,
        "machine",
        1024,
        command_queue,
        tskIDLE_PRIORITY + 2,
        NULL
    );
    xTaskCreate(
        serial_task,
        "serial",
        1024,
        command_queue,
        tskIDLE_PRIORITY + 1,
        NULL
    );
    vTaskStartScheduler();

    while (true) {
    }
}
