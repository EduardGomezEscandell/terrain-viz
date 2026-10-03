cmake_minimum_required(VERSION 3.15...4.2)
project(elevation LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra -Wpedantic -Werror)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)
find_package(TBB REQUIRED)

include_directories(elevation/cxx)
add_subdirectory(elevation/cxx)
