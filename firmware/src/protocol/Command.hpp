#pragma once

#include <cstdint>

enum class AxisId : uint8_t {
    XL,
    YL,
    XR,
    YR,
};

enum class CommandType : uint8_t {
    Invalid,
    Hello,
    Status,
    Jog,
    SetZero,
    Move4,
    RunBegin,
    RunEnd,
    Stop,
};

struct JogCommand {
    AxisId axis;
    float distance_mm;
    float feedrate_mm_min;
};

struct Move4Command {
    float xl_mm;
    float yl_mm;
    float xr_mm;
    float yr_mm;
    float feedrate_mm_min;
};

struct Command {
    CommandType type = CommandType::Invalid;

    union {
        JogCommand jog;
        Move4Command move4;
    } data;
};
