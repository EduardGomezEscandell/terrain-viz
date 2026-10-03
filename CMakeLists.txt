cmake_minimum_required(VERSION 3.15...4.2)
project(elevation LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

include_directories(elevation/cxx)
add_subdirectory(elevation/cxx)