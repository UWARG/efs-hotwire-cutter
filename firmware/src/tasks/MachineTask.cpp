#include "tasks/MachineTask.hpp"

#include <stdio.h>

#include "FreeRTOS.h"
#include "queue.h"
#include "task.h"

#include "protocol/Command.hpp"

namespace {

enum class MachineState {
    NeedZero,
    Idle,
};

const char *state_name(MachineState state)
{
    return state == MachineState::NeedZero ? "NEED_ZERO" : "IDLE";
}

class MachineController {
public:
    MachineController(QueueHandle_t command_queue)
        : command_queue_(command_queue)
    {
    }

    void handle(const Command &command)
    {
        switch (command.type) {
        case CommandType::Hello:
            printf("ACK\n");
            return;

        case CommandType::Status:
            print_status();
            return;

        case CommandType::SetZero:
            state_ = MachineState::Idle;
            printf("OK CMD=SET_ZERO\n");
            return;

        case CommandType::Jog:
        case CommandType::Move4:
            printf("\n");
            return;

        case CommandType::Invalid:
            printf("INVALID\n");
            return;
        }
    }

private:
    void print_status() const
    {
        const UBaseType_t used = uxQueueMessagesWaiting(command_queue_);
        const UBaseType_t free = uxQueueSpacesAvailable(command_queue_);
        const unsigned zeroed = ( (state_ == MachineState::Idle) ? 1U : 0U);

        printf(
            "STATUS STATE=%s ZEROED=%u XL=0.000 YL=0.000 XR=0.000 YR=0.000 "
            "BUFFER_FREE=%u BUFFER_USED=%u\n",
            state_name(state_),
            zeroed,
            static_cast<unsigned>(free),
            static_cast<unsigned>(used)
        );
    }

    QueueHandle_t command_queue_;
    MachineState state_ = MachineState::NeedZero;
};

} // namespace

void machine_task(void *params)
{
    auto command_queue = static_cast<QueueHandle_t>(params);
    MachineController machine(command_queue);
    Command command;

    while (true) {
        if (xQueueReceive(command_queue, &command, portMAX_DELAY) == pdTRUE) {
            machine.handle(command);
        }
    }
}
