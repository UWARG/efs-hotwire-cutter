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
    Running,
};

struct MachinePosition {
    float xl_mm = 0.0f;
    float yl_mm = 0.0f;
    float xr_mm = 0.0f;
    float yr_mm = 0.0f;
};

const char *state_name(MachineState state)
{
    switch (state) {
    case MachineState::NeedZero:
        return "NEED_ZERO";
    case MachineState::Idle:
        return "IDLE";
    case MachineState::Running:
        return "RUNNING";
    }

    return "?";
}

void zero_position(MachinePosition &position)
{
    position = {};
}

void apply_jog(MachinePosition &position, const JogCommand &jog)
{
    switch (jog.axis) {
    case AxisId::XL:
        position.xl_mm += jog.distance_mm;
        return;
    case AxisId::YL:
        position.yl_mm += jog.distance_mm;
        return;
    case AxisId::XR:
        position.xr_mm += jog.distance_mm;
        return;
    case AxisId::YR:
        position.yr_mm += jog.distance_mm;
        return;
    }
}

void apply_move4(MachinePosition &position, const Move4Command &move4)
{
    position.xl_mm = move4.xl_mm;
    position.yl_mm = move4.yl_mm;
    position.xr_mm = move4.xr_mm;
    position.yr_mm = move4.yr_mm;
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
            zero_position(position_);
            state_ = MachineState::Idle;
            printf("OK CMD=SET_ZERO\n");
            return;

        case CommandType::RunBegin:
            state_ = MachineState::Running;
            printf("OK CMD=RUN_BEGIN\n");
            return;

        case CommandType::RunEnd:
            state_ = MachineState::Idle;
            printf("OK CMD=RUN_END\n");
            return;

        case CommandType::Stop:
            state_ = MachineState::Idle;
            printf("OK CMD=STOP\n");
            return;

        case CommandType::Jog:
            apply_jog(position_, command.data.jog);
            printf("OK CMD=JOG\n");
            return;

        case CommandType::Move4:
            apply_move4(position_, command.data.move4);
            printf("OK CMD=MOVE4\n");
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
        const unsigned zeroed = (state_ == MachineState::NeedZero) ? 0U : 1U;

        printf(
            "STATUS STATE=%s ZEROED=%u XL=%.3f YL=%.3f XR=%.3f YR=%.3f "
            "BUFFER_FREE=%u BUFFER_USED=%u\n",
            state_name(state_),
            zeroed,
            static_cast<double>(position_.xl_mm),
            static_cast<double>(position_.yl_mm),
            static_cast<double>(position_.xr_mm),
            static_cast<double>(position_.yr_mm),
            static_cast<unsigned>(free),
            static_cast<unsigned>(used)
        );
    }

    QueueHandle_t command_queue_;
    MachineState state_ = MachineState::NeedZero;
    MachinePosition position_;
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
