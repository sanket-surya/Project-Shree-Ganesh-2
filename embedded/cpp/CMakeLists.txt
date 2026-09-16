-+cmake_minimum_required(VERSION 3.14)
project(AeroPistonDigitalTwin CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Original standalone simulator
add_executable(aero_twin_sim
    main_sim.cpp
    aero_twin_engine.cpp
    aero_twin_engine.hpp
)
target_include_directories(aero_twin_sim PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# C++ WebSocket Bridge — React GCS Dashboard (Port 9001)
add_executable(cpp_ws_bridge
    cpp_ws_bridge.cpp
    aero_twin_engine.cpp
    aero_twin_engine.hpp
    ws_server.hpp
)
target_include_directories(cpp_ws_bridge PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# WinSock2 — built-in, no install needed
if(WIN32)
    target_link_libraries(cpp_ws_bridge PRIVATE ws2_32)
    target_link_libraries(aero_twin_sim PRIVATE ws2_32)
endif()
