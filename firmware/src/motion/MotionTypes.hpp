#pragma once

#include <cstdint>

struct MotionSegment {
    int32_t xlSteps = 0;
    int32_t ylSteps = 0;
    int32_t xrSteps = 0;
    int32_t yrSteps = 0;

    uint32_t tickCount = 0;
};

struct AxesToStep {
    bool xl = false;
    bool yl = false;
    bool xr = false;
    bool yr = false;
};
