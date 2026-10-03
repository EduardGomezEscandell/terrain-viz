#include <cassert>
#include <cstdio>
#include <pybind11/buffer_info.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <stdexcept>

namespace py = pybind11;


void raytrace(py::buffer array, float scale, float sun_altitude, float sun_azimuth) {
    const py::buffer_info info = array.request();
    if (info.ndim != 2) {
        throw std::runtime_error("Input buffer must have two dimension");
    }
    
    printf(
        "rows: %lu cols: %lu scale: %f sun_altitude: %f  sun_azimuth: %f\n",
        info.shape[0], info.shape[1], scale, sun_altitude, sun_azimuth
    );
    fflush(stdout);



}
