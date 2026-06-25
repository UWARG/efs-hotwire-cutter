#include "tasks/SerialTask.hpp"

#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "pico/stdio.h"
#include "pico/stdlib.h"

#include "FreeRTOS.h"
#include "task.h"

namespace {

constexpr size_t kLineBufferLength = (1 << 8); // 2^8 = 256

TaskHandle_t serial_task_handle = nullptr;

void on_stdio_chars_available(void *param)
{
    (void)param;

    if (serial_task_handle == nullptr) {
        return;
    }

    BaseType_t higher_priority_task_woken = pdFALSE;
    vTaskNotifyGiveFromISR(serial_task_handle, &higher_priority_task_woken);
    portYIELD_FROM_ISR(higher_priority_task_woken); 
}

void handle_command(const char *line)
{
    //eventually will add support for CUT4, MOVE4, SET_TEMP and STOP
    if (strcmp(line, "HELLO") == 0) {
        printf("ACK\n");
        return;
    }

    if (strcmp(line, "STATUS?") == 0) {
        printf("STATUS STATE=? ZEROED=? BUFFER_FREE=?\n");
        return;
    }

    printf("INVALID COMMAND\n");
}

void handle_received_char(
    int ch,
    char line_buffer[],
    size_t &line_length,
    bool &line_overflowed
)
{
    if (ch == '\r') {
        return;
    }

    if (ch == '\n') {
        if (line_overflowed) {
            line_overflowed = false;
            line_length = 0;
            return;
        }

        line_buffer[line_length] = '\0';
        handle_command(line_buffer);
        line_length = 0;
        return;
    }

    if (line_overflowed) {
        return;
    }

    if (line_length >= kLineBufferLength - 1) {
        printf("ERR: Line too Long\n");
        line_length = 0;
        line_overflowed = true;
        return;
    }

    line_buffer[line_length] = static_cast<char>(ch);
    ++line_length;
}

void drain_available_chars(
    char line_buffer[],
    size_t &line_length,
    bool &line_overflowed
)
{
    int ch;
    while ((ch = getchar_timeout_us(0)) != PICO_ERROR_TIMEOUT) {
        handle_received_char(ch, line_buffer, line_length, line_overflowed);
    }
}

} // namespace

void serial_task(void *params)
{
    (void)params;

    char line_buffer[kLineBufferLength] = {};
    size_t line_length = 0;
    bool line_overflowed = false;

    serial_task_handle = xTaskGetCurrentTaskHandle();
    stdio_set_chars_available_callback(on_stdio_chars_available, nullptr);
    printf("READY\n");

    while (true) {
        drain_available_chars(line_buffer, line_length, line_overflowed);
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    }
}
