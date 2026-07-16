#pragma once

#include "MotionTypes.hpp"

class DdaStepper {
public:
    void start(const MotionSegment& segment);
    AxisMask nextTick();
    bool done() const;

private:
    AxisStepCounts direction = {};
    AxisStepCounts errorFactor = {};
    uint32_t tickIndex = 0;
    uint32_t expectedSteps = 0;
};
