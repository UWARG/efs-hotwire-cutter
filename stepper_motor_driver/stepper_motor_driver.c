#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/uart.h"



// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
// --- X-Axis Pin Definitions (SKR Pico Layout) ---
#define X_STEP_PIN      6
#define X_DIR_PIN       5
#define X_ENABLE_PIN    7
#define X_UART_ADDR  0

// --- Y-Axis Pin Definitions (SKR Pico Layout) ---
#define Y_STEP_PIN      14
#define Y_DIR_PIN       13
#define Y_ENABLE_PIN    15
#define Y_UART_ADDR     1  // Y-axis is Node Address 1 on the shared UART bus
    
#define UART_TX_PIN 8
#define UART_RX_PIN 9

#define VM_UART         uart1
#define MOTOR_STEPS_PER_REV 200
#define MICROSTEPS          8
#define STEPS_PER_REV       (MOTOR_STEPS_PER_REV * MICROSTEPS) // 3200 steps

#define SGTHRS_VALUE 128 // idk what this does for SGTHRS we're just going to use the middle value for now because that seems the most correct XD
#define SG_RESULT_THRESHOLD 67 // any SG_RESULT value lower than this will be considered a stall

#define SGTHRS 0x40 // address of the stall guard threshold register, higher = more sensitive detection of stalling, min 0 max 255
#define SG_RESULT 0x41 // StallGuard4 generates a value, goes from 0 to 510 with 0 being highest load and 510 being lowest load

const uint32_t FIXED_SPEED_DELAY_US = 1000;
//set to match motor
const float X_MM_PER_REV = 1.5875f; // 1.5875mm per revolution for the lead screw
const float Y_MM_PER_REV = 1.5875f; // 1.5875mm per revolution for the lead screw

uint8_t calculateCRC(uint8_t* datagram, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        uint8_t currentByte = datagram[i];
        for (uint8_t j = 0; j < 8; j++) {
            if ((crc >> 7) ^ (currentByte & 0x01)) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
            currentByte >>= 1;
        }
    }
    return crc;
}

uint32_t readTMCRegister(uint8_t target_address, uint8_t reg) {
    uint8_t packet[4];
    uint32_t result = 0;

    packet[0] = 0x05;         // Sync bits
    packet[1] = target_address;         // X-axis node address
    packet[2] = reg | 0x80;   // Add write flag bit
    packet[3] = calculateCRC(packet, 4);
    
    uart_write_blocking(VM_UART, packet, sizeof(packet)); // send read request
    uart_read_blocking(VM_UART, (uint8_t*)(&result), sizeof(result));
    return result;
}

void writeTMCRegister(uint8_t target_address, uint8_t reg, uint32_t data)
{
    uint8_t packet[4];
    packet[0] = 0x05;         // Sync bits
    packet[1] = target_address;         // X-axis node address
    packet[2] = reg | 0x80;   // Add write flag bit
    
    packet[3] = (data >> 24) & 0xFF;
    packet[4] = (data >> 16) & 0xFF;
    packet[5] = (data >> 8)  & 0xFF;
    packet[6] = data & 0xFF;
    
    packet[7] = calculateCRC(packet, 7);
}


void move_X(float distance_mm){
    bool dir = (distance_mm >= 0);
    float absolute_distance = fabsf(distance_mm);
    //(distance/mm_per_turn) *steps_per_turn
    uint32_t total_steps = (uint32_t)((absolute_distance / X_MM_PER_REV) * STEPS_PER_REV);

    gpio_put(X_DIR_PIN, dir);

    for (uint32_t i = 0; i < total_steps; ++i){
        gpio_put(X_STEP_PIN, true);
        sleep_us(2);
        gpio_put(X_STEP_PIN, false);
        sleep_us(FIXED_SPEED_DELAY_US);
    }
}

bool isMotorBlocked()
{
    return readTMCRegister(X_UART_ADDR, SG_RESULT) <= SG_RESULT_THRESHOLD;
}

int main()
{
    stdio_init_all();

    uart_init(VM_UART, 115200);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_format(VM_UART, 8, 1, UART_PARITY_NONE);

    // 3. Initialize Pins for X Axis
    gpio_init(X_STEP_PIN);
    gpio_set_dir(X_STEP_PIN, GPIO_OUT);
    
    gpio_init(X_DIR_PIN);
    gpio_set_dir(X_DIR_PIN, GPIO_OUT);
    
    gpio_init(X_ENABLE_PIN);
    gpio_set_dir(X_ENABLE_PIN, GPIO_OUT);
    
    // Enable pin is inverted logic. Setting it to FALSE powers up the motor coils.
    gpio_put(X_ENABLE_PIN, false); 
    sleep_ms(10); // Quick stability delay

    // 4. Send safety configuration registers to the X-Axis Driver (Node Address 0)
    // 4. Send safety configuration registers to the X-Axis Driver (Node Address 0)
    writeTMCRegister(X_UART_ADDR, 0x10, 0x00001F10); // Sets conservative, safe operating currents
    writeTMCRegister(X_UART_ADDR, 0x6C, 0x04000053); // Configures smooth 16 microsteps (dedge = 0)
    writeTMCRegister(X_UART_ADDR, SGTHRS, SGTHRS_VALUE);

    sleep_ms(1000); // Wait 1 second before beginning test routine
    // 5. Main Test Loop

    // Move 5mm to the right (positive)
    move_X(1.5875f);
    
    // Stop completely for 1.5 seconds
    sleep_ms(1500);
    
    // Move 5mm to the left (negative)
    move_X(-1.5875f);
    
    // Stop completely for 1.5 seconds before repeating
    sleep_ms(1500);

    // test the driving of the pin
    gpio_put(X_DIR_PIN, false);
    while (true)
    {
        printf("SG_RESULT: %d\n", readTMCRegister(X_UART_ADDR, SG_RESULT));
        gpio_put(X_STEP_PIN, true);
        sleep_us(2);
        gpio_put(X_STEP_PIN, false);
        sleep_us(FIXED_SPEED_DELAY_US);
    }
}
