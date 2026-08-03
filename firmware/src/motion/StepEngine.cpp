

#include "StepEngine.hpp"

// Constructor
StepEngine::StepEngine(StepDirDriver& driver)
    : driver_(driver), state_(StepEngineState::Idle) {}

// Initialize driver, disable motor outputs for safety, and set state
void StepEngine::init() {
    driver_.init();
    driver_.disableAll(); // Disable drivers on startup for safety
    state_ = StepEngineState::Idle;
}

// Prepare motor state and start DDA segment execution
bool StepEngine::start(const MotionSegment& segment) {
    if (state_ == StepEngineState::Running) {
        return false; // Engine is busy
    }

    // 1. Initialize the DDA calculation with the segment
    dda_.start(segment);

    // 2. Set direction pins from the segment parameter
    driver_.setDirections(segment.directionPositive);

    // 3. Enable motor power outputs
    driver_.enableAll();

    // 4. Update internal state
    state_ = StepEngineState::Running;
    return true;
}

// Stop execution, disable motor outputs, and return to Idle
void StepEngine::stop() {
    driver_.disableAll();
    state_ = StepEngineState::Idle;
}

// Return current engine state
StepEngineState StepEngine::state() const {
    return state_;
}

// Timer tick function: handles per-step decisions and pulse triggering
void StepEngine::tick() {
    if (state_ != StepEngineState::Running) {
        return;
    }

    // 1. Ask DDA which motors need a step pulse right now
    AxisMask mask = dda_.nextTick();

    // 2. Call the driver to execute the pulse for those motors
    driver_.pulse(mask);

    // 3. Ask DDA if the segment is finished; if so, stop the engine
    if (dda_.done()) {
        stop();
    }
}