#pragma once

#include "DdaStepper.hpp"
#include "../drivers/StepDirDriver.hpp"

enum class StepEngineState {
    Idle,
    Running,
    Faulted,
};

class StepEngine {
public:
    explicit StepEngine(StepDirDriver& driver);

    void init();
    bool start(const MotionSegment& segment);
    void stop();
    StepEngineState state() const;

private:
    StepDirDriver& driver_;
    DdaStepper dda_;
    StepEngineState state_ = StepEngineState::Idle;
};
