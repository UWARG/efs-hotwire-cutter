#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/uart.h"



// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define X_STEP_PIN      11
#define X_DIR_PIN       10
#define X_ENABLE_PIN    12
#define X_UART_ADDR  0
#define UART_TX_PIN 8
#define UART_RX_PIN 9

#define VM_UART         uart1
#define MOTOR_STEPS_PER_REV 200
#define MICROSTEPS          16
#define STEPS_PER_REV       (MOTOR_STEPS_PER_REV * MICROSTEPS) // 3200 steps

const uint32_t FIXED_SPEED_DELAY_US = 1000;
//set to match motor
const float X_MM_PER_REV = 40.0;

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

void writeTMCRegister(uint8_t target_address, uint8_t reg, uint32_t data) {
    uint8_t packet[8];
    packet[0] = 0x05;         // Sync bits
    packet[1] = target_address;         // X-axis node address
    packet[2] = reg | 0x80;   // Add write flag bit
    
    packet[3] = (data >> 24) & 0xFF;
    packet[4] = (data >> 16) & 0xFF;
    packet[5] = (data >> 8)  & 0xFF;
    packet[6] = data & 0xFF;
    
    packet[7] = calculateCRC(packet, 7);
    
    // Direct hardware write via Pico SDK tracking
    uart_write_blocking(VM_UART, packet, 8);
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
    writeTMCRegister(X_UART_ADDR, 0x10, 0x00001F10); // Sets conservative, safe operating currents
    writeTMCRegister(X_UART_ADDR, 0x6C, 0x14000053); // Configures smooth 16 microsteps

    sleep_ms(1000); // Wait 1 second before beginning test routine

    // 5. Main Test Loop

    // Move 5mm to the right (positive)
    move_X(1.0f);
    
    // Stop completely for 1.5 seconds
    sleep_ms(1500);
    
    // Move 5mm to the left (negative)
    move_X(-1.0f);
    
    // Stop completely for 1.5 seconds before repeating
    sleep_ms(1500);

}
