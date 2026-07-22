#pragma once

#include "MotionTypes.hpp"

class DdaStepper {
public:
    void start(const MotionSegment& segment);
    AxisMask nextTick();
    bool done() const;

private:
    AxisStepCounts direction = {};

    // error terms
    int32_t exl = 0;
    int32_t exr = 0;
    int32_t eyl = 0;
    int32_t eyr = 0;

    uint32_t tickIndex = 0;
    uint32_t expectedSteps = 0;
};
