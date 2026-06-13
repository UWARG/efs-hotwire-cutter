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
    void setDirections(bool xlPositive, bool ylPositive, bool xrPositive, bool yrPositive);
    void pulse(AxesToStep axes);
};
