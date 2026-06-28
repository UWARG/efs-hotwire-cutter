#pragma once

#include <cstdint>

struct AxisStepCounts {
    uint32_t xl = 0;
    uint32_t yl = 0;
    uint32_t xr = 0;
    uint32_t yr = 0;
};

struct AxisMask {
    bool xl = false;
    bool yl = false;
    bool xr = false;
    bool yr = false;
};

struct MotionSegment {
    AxisStepCounts steps{};
    AxisMask directionPositive{};
    uint32_t dominantSteps = 0;
    uint32_t tickIntervalUs = 0;
};
