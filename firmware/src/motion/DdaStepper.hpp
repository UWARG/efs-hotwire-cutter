#pragma once

#include "MotionTypes.hpp"

class DdaStepper {
public:
    void start(const MotionSegment& segment);
    AxesToStep nextTick();
    bool done() const;

private:
    MotionSegment segment{};
    uint32_t tickIndex = 0;
};
