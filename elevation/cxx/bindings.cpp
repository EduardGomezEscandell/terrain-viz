#include <pybind11/pybind11.h>
#include "raytrace.hpp"

PYBIND11_MODULE(raytrace, m, pybind11::mod_gil_not_used()) {
    m.doc() = "pybind11 raytrace plugin";

    m.def("raytrace", &raytrace, "A function that computes shadows on an elevation map");
}