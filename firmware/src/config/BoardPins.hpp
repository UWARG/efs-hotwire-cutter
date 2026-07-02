#pragma once

#include <cstdint>

namespace pins {

// BigTreeTech SKR Pico motor driver control pins
constexpr uint8_t X_ENABLE_PIN = 12;
constexpr uint8_t X_STEP_PIN = 11;
constexpr uint8_t X_DIR_PIN = 10;

constexpr uint8_t Y_ENABLE_PIN = 7;
constexpr uint8_t Y_STEP_PIN = 6;
constexpr uint8_t Y_DIR_PIN = 5;

constexpr uint8_t Z_ENABLE_PIN = 2;
constexpr uint8_t Z_STEP_PIN = 19;
constexpr uint8_t Z_DIR_PIN = 28;

constexpr uint8_t E0_ENABLE_PIN = 15;
constexpr uint8_t E0_STEP_PIN = 14;
constexpr uint8_t E0_DIR_PIN = 13;

constexpr uint8_t MOTOR_UART_RX_PIN = 9;
constexpr uint8_t MOTOR_UART_TX_PIN = 8;

} // namespace pins
