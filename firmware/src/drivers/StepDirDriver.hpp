#pragma once

#include "../motion/MotionTypes.hpp"

class StepDirDriver {
public:
    StepDirDriver(
        bool xlDirInverted,
        bool ylDirInverted,
        bool xrDirInverted,
        bool yrDirInverted
    );

    void init();
    void enableAll();
    void disableAll();
    void setDirections(AxisMask directionPositive);
    void pulse(AxisMask axesToStep);
};
