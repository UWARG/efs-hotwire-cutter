# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

set(HOTWIRE_FREERTOS_KERNEL_PATH ${CMAKE_CURRENT_LIST_DIR}/external/FreeRTOS-Kernel)

if(EXISTS "${HOTWIRE_FREERTOS_KERNEL_PATH}")
    set(FREERTOS_KERNEL_PATH ${HOTWIRE_FREERTOS_KERNEL_PATH})
elseif(DEFINED ENV{FREERTOS_KERNEL_PATH})
    set(FREERTOS_KERNEL_PATH $ENV{FREERTOS_KERNEL_PATH})
endif()

if(FREERTOS_KERNEL_PATH)
    set(FREERTOS_IMPORT ${FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)
    if(EXISTS "${FREERTOS_IMPORT}")
        include("${FREERTOS_IMPORT}")
        set(HOTWIRE_FREERTOS_AVAILABLE 1)
    else()
        message(STATUS "FREERTOS_KERNEL_PATH is set, but RP2040 import file was not found: ${FREERTOS_IMPORT}")
    endif()
else()
    message(STATUS "FreeRTOS kernel not found; building without FreeRTOS until the kernel path is configured")
endif()

project(hotwire_firmware C CXX ASM)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

add_executable(hotwire_firmware
        src/main.cpp
        src/tasks/SerialTask.cpp
        )

pico_set_program_name(hotwire_firmware "hotwire_firmware")
pico_set_program_version(hotwire_firmware "0.1")

# Modify the below lines to enable/disable output over UART/USB
pico_enable_stdio_uart(hotwire_firmware 0)
pico_enable_stdio_usb(hotwire_firmware 1)

# Add the standard library to the build
target_link_libraries(hotwire_firmware
        pico_stdlib)

# Add the standard include files to the build
target_include_directories(hotwire_firmware PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
        ${CMAKE_CURRENT_LIST_DIR}/src
        ${CMAKE_CURRENT_LIST_DIR}/freertos
)

# Add any user requested libraries
target_link_libraries(hotwire_firmware 
        hardware_timer
        )

if(HOTWIRE_FREERTOS_AVAILABLE)
    target_link_libraries(hotwire_firmware
            FreeRTOS-Kernel
            FreeRTOS-Kernel-Heap4
            )
endif()

pico_add_extra_outputs(hotwire_firmware)
