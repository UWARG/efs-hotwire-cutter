#include "DdaStepper.hpp"

inline uint32_t max(uint32_t a, uint32_t b) {
    return (a > b) ? a : b;
}

void DdaStepper::start(const MotionSegment& segment) {
    direction = segment.steps;
    tickIndex = 0;
    expectedSteps = max(max(direction.xl, direction.xr), max(direction.yl, direction.yr));
    errorFactor = {
        2 * direction.xl - expectedSteps,
        2 * direction.xr - expectedSteps,
        2 * direction.yl - expectedSteps,
        2 * direction.yr - expectedSteps
    };
}

AxisMask DdaStepper::nextTick() {
    if (done()) {
        return {0, 0, 0, 0};
    }

    uint32_t exl = errorFactor.xl;
    uint32_t exr = errorFactor.xr;
    uint32_t eyl = errorFactor.yl;
    uint32_t eyr = errorFactor.yr;

    uint32_t dxl = direction.xl;
    uint32_t dxr = direction.xr;
    uint32_t dyl = direction.yl;
    uint32_t dyr = direction.yr;

    AxisMask result = {
        exl > 0,
        exr > 0,
        eyl > 0,
        eyr > 0
    };

    errorFactor = {
        (exl > 0) ? (2 * (dxl - expectedSteps)) : (2 * dxl),
        (exr > 0) ? (2 * (dxr - expectedSteps)) : (2 * dxr),
        (eyl > 0) ? (2 * (dyl - expectedSteps)) : (2 * dyl),
        (eyr > 0) ? (2 * (dyr - expectedSteps)) : (2 * dyr)
    };

    return result;
}

bool DdaStepper::done() const {
    return tickIndex == expectedSteps;
}