#include <pybind11/pybind11.h>

void raytrace_fixedsource(pybind11::buffer input, pybind11::buffer output,
                          float scale, float sun_azimuth, float sun_altitude,
                          float eye_level, unsigned int subsampling_level);

void raytrace_cartographic(pybind11::buffer input_buff,
                           pybind11::buffer output_buff, float scale,
                           float bottom_northing, float left_easting,
                           long long int seconds_since_epoch, float eye_level,
                           unsigned int subsampling_level);