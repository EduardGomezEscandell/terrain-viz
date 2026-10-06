#include <pybind11/pybind11.h>
#include "raytrace.hpp"

PYBIND11_MODULE(raytrace, m, pybind11::mod_gil_not_used()) {
    m.doc() = "pybind11 raytrace plugin";

    m.def("raytrace_fixedsource", &raytrace_fixedsource,
          "Compute shadow coverage with a fixed light source, optionally subsampling ray origins per pixel");
    
    m.def("raytrace_cartographic", &raytrace_cartographic,
          "Compute shadow coverage with a latitude/longitude/timestamp, optionally subsampling ray origins per pixel");
}