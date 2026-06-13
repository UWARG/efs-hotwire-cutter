#pragma once

#include <cstdint>

namespace pins {

}


struct StepDirPins {
    uint8_t step = 0;
    uint8_t dir = 0;
    uint8_t enable = 0;
};

struct BoardPins {
    StepDirPins xl{};
    StepDirPins yl{};
    StepDirPins xr{};
    StepDirPins yr{};
};
