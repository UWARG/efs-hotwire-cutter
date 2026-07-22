#include "DdaStepper.hpp"

inline uint32_t max(uint32_t a, uint32_t b) {
    return (a > b) ? a : b;
}

void DdaStepper::start(const MotionSegment& segment) {
    direction = segment.steps;
    tickIndex = 0;
    expectedSteps = max(max(direction.xl, direction.xr), max(direction.yl, direction.yr));
    exl = 2 * direction.xl - expectedSteps;
    eyl = 2 * direction.yl - expectedSteps;
    exr = 2 * direction.xr - expectedSteps;
    eyr = 2 * direction.yr - expectedSteps;
}

AxisMask DdaStepper::nextTick() {
    if (done()) {
        return {0, 0, 0, 0};
    }

    uint32_t dxl = direction.xl;
    uint32_t dyl = direction.yl;
    uint32_t dxr = direction.xr;
    uint32_t dyr = direction.yr;

    AxisMask result = {
        exl > 0,
        eyl > 0,
        exr > 0,
        eyr > 0
    };

    exl = (exl > 0) ? (2 * (dxl - expectedSteps)) : (2 * dxl);
    eyl = (eyl > 0) ? (2 * (dyl - expectedSteps)) : (2 * dyl);
    exr = (exr > 0) ? (2 * (dxr - expectedSteps)) : (2 * dxr);
    eyr = (eyr > 0) ? (2 * (dyr - expectedSteps)) : (2 * dyr);

    tickIndex++;
    
    return result;
}

bool DdaStepper::done() const {
    return tickIndex == expectedSteps;
}