#include "DdaStepper.hpp"

inline uint32_t max(uint32_t a, uint32_t b) {
    return (a > b) ? a : b;
}

void DdaStepper::start(const MotionSegment& segment) {
    steps = segment.steps;
    tickIndex = 0;
    expectedSteps = max(max(steps.xl, steps.xr), max(steps.yl, steps.yr));
    exl = 2 * steps.xl - expectedSteps;
    eyl = 2 * steps.yl - expectedSteps;
    exr = 2 * steps.xr - expectedSteps;
    eyr = 2 * steps.yr - expectedSteps;
}

AxisMask DdaStepper::nextTick() {
    if (done()) {
        return {0, 0, 0, 0};
    }

    uint32_t dxl = steps.xl;
    uint32_t dyl = steps.yl;
    uint32_t dxr = steps.xr;
    uint32_t dyr = steps.yr;

    AxisMask result = {
        exl > 0,
        eyl > 0,
        exr > 0,
        eyr > 0
    };

    exl += (exl > 0) ? (2 * (dxl - expectedSteps)) : (2 * dxl);
    eyl += (eyl > 0) ? (2 * (dyl - expectedSteps)) : (2 * dyl);
    exr += (exr > 0) ? (2 * (dxr - expectedSteps)) : (2 * dxr);
    eyr += (eyr > 0) ? (2 * (dyr - expectedSteps)) : (2 * dyr);

    tickIndex++;
    
    return result;
}

bool DdaStepper::done() const {
    return tickIndex == expectedSteps;
}
