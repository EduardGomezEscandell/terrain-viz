#include <pybind11/pybind11.h>

void raytrace(pybind11::buffer input, pybind11::buffer output, float scale,
              float sun_azimuth, float sun_altitude, float eye_level);