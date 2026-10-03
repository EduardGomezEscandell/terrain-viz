#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <execution>
#include <limits>
#include <numeric>
#include <pybind11/buffer_info.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <random>
#include <stdexcept>
#include <tbb/blocked_range.h>
#include <tbb/parallel_for.h>

// #define DEBUG_PRINTS 1

#ifdef DEBUG_PRINTS
#define debug_printf printf
#else
void nothing(char const *, ...) {};
#define debug_printf nothing
#endif

namespace py = pybind11;
using Vec = std::array<float, 3>;

// Consistent seed so that creating animations does not produce noise
thread_local std::mt19937 jitter_generator(123456);
thread_local std::normal_distribution<float> jitter_dist(0.0, 0.05);

struct spatial_data {
  py::buffer_info const &buff;
  float scale;
  std::array<float, 3> direction;
};

struct Loc {
  ssize_t i; // Pixel row
  ssize_t j; // Pixel col
  Vec pos;   // Position: x,y are relative to the center of the pixel. z is
             // elevation.

  void print_debug() {
    debug_printf("Location is pixel [%ld, %ld], coords (%f, %f, %f)\n", i, j,
                 pos[0], pos[1], pos[2]);
  }
};

float buffer_at(py::buffer_info const &buff, ssize_t i, ssize_t j) {
  const auto ncols = buff.shape[1];
  return static_cast<float *>(buff.view()->buf)[i * ncols + j];
}

std::tuple<ssize_t, ssize_t> buffer_size(py::buffer_info const &buff) {
  return std::make_tuple(buff.shape[0], buff.shape[1]);
}

float safe_divide(float num, float denom) {
  if (denom > -1e-5 && denom < 1e-5) {
    return std::numeric_limits<float>::max();
  }
  return num / denom;
}

void advance(spatial_data const &sd, Loc &location) {
  // Reading the direction we move we can tell what two possible edges we may
  // exit the pixel through
  const int vx_sign = sd.direction[0] > 0 ? 1 : -1;
  const int vy_sign = sd.direction[1] > 0 ? 1 : -1;

  const float edge_x = vx_sign * 0.5;
  const float edge_y = vy_sign * 0.5;

  // Tajectory is parametrized as s(t) = pos + direction*t.
  //  - t_h is the h parameter at which the ray hits the vertical edge of the
  //  pixel.
  //  - t_y is the h parameter at which the ray hits the horizontal edge of the
  //  pixel.
  // We take the minimum, as that is where the ray exits the pixel
  const float t_x = safe_divide(edge_x - location.pos[0], sd.direction[0]);
  const float t_y = safe_divide(edge_y - location.pos[1], sd.direction[1]);

  if (t_x < t_y) {
    // We move to the pixel to the right/left
    location.i += vx_sign;

    // Update local coordinates
    location.pos[0] = -vx_sign * 0.5;
    location.pos[1] += sd.direction[1] * t_x;
    location.pos[2] += sd.direction[2] * t_x;
  } else {
    // We move to the pixel up/down
    location.j += vy_sign;

    // Update local coordinates
    location.pos[0] += sd.direction[0] * t_y;
    location.pos[1] = -vy_sign * 0.5;
    location.pos[2] += sd.direction[2] * t_y;
  }
}

/**
 * Cast a ray starting at location. Returns true if it escapes without
 * intersecting the terrain
 */
bool cast_single_ray(spatial_data const &sd, Loc &location) {
  const auto [nrows, ncols] = buffer_size(sd.buff);

  location.print_debug();

  for (ssize_t i = 0; i < nrows + ncols + 1; ++i) {
    advance(sd, location);

    location.print_debug();

    if (location.i < 0 || location.i >= nrows) {
      debug_printf("Escaping x\n");
      // Ray escaped!
      return true;
    }

    if (location.j < 0 || location.j >= ncols) {
      debug_printf("Escaping y\n");
      // Ray escaped!
      return true;
    }

    if (buffer_at(sd.buff, location.i, location.j) > location.pos[2]) {
      // Ray is under terrain! Return false
      debug_printf("Escaping z\n");
      return false;
    }
  }

  throw std::runtime_error("Raytrace not converging!");
}

std::vector<Loc> ray_start(py::buffer_info const &buff, ssize_t i, ssize_t j,
                           float eye_level, uint subsampling_level) {
  const float z = buffer_at(buff, i, j) + eye_level;

  switch (subsampling_level) {
  case 0: // Central
    return {Loc{i, j, {-0.0, -0.0, z}}};
  case 1: // Rombus
    return {Loc{i, j, {0.00, -0.33, z}}, Loc{i, j, {0.00, 0.33, z}},
            Loc{i, j, {-0.33, 0.00, z}}, Loc{i, j, {0.33, 0.00, z}}};
  case 2: // Rhombus, jiggled
  {
    std::vector L = {Loc{i, j, {0.00, -0.33, z}}, Loc{i, j, {0.00, 0.33, z}},
                     Loc{i, j, {-0.33, 0.00, z}}, Loc{i, j, {0.33, 0.00, z}}};

    // Reset the seed so that re-running the same image yields the same
    // subpixels
    jitter_generator.seed(i * buff.shape[1] + j);
    jitter_dist.reset();

    for (auto &loc : L) {
      loc.pos[0] =
          std::clamp(loc.pos[0] + jitter_dist(jitter_generator), -0.45f, 0.45f);
      loc.pos[1] =
          std::clamp(loc.pos[1] + jitter_dist(jitter_generator), -0.45f, 0.45f);
    }

    return L;
  }
  case 3:

  default:
    throw std::runtime_error("Chosen Subsampling level does not exist");
  }
}

void raytrace(py::buffer input_buff, py::buffer output_buff, float scale,
              float sun_azimuth, float sun_altitude, float eye_level,
              uint subsampling_level) {
  const auto input = input_buff.request();
  const auto output = output_buff.request(true);

  if (input.ndim != 2) {
    throw std::runtime_error("Input buffer must have two dimension");
  }
  if (output.ndim != 2) {
    throw std::runtime_error("Output buffer must have two dimension");
  }

  const auto [inrows, incols] = buffer_size(input);
  const auto [ourows, oucols] = buffer_size(output);
  if (inrows != ourows || incols != oucols) {
    throw std::runtime_error("Input and output must have the same shape");
  }

  const auto az = sun_azimuth * M_PI / 180;
  const auto at = sun_altitude * M_PI / 180;

  const spatial_data sd{.buff = input,
                        .scale = scale,
                        .direction = {
                            (static_cast<float>(-std::cos(at) * std::cos(az))),
                            (static_cast<float>(std::cos(at) * std::sin(az))),
                            (static_cast<float>(std::sin(at))) * scale,
                        }};

  debug_printf("Ray direction is (%f,%f,%f)", sd.direction[0], sd.direction[1],
               sd.direction[2]);

  auto out_begin = static_cast<float *>(output.ptr);
  std::transform(
      std::execution::par_unseq, out_begin, out_begin + input.size, out_begin,
      [&](float &cursor) -> float {
        debug_printf("\n------------------\n");
        const ssize_t flat_index = &cursor - out_begin;
        const ssize_t i = flat_index / incols;
        const ssize_t j = flat_index % incols;

        auto subpixels = ray_start(sd.buff, i, j, eye_level, subsampling_level);

        const int lit_subpixels = std::transform_reduce(
            std::execution::unseq, subpixels.cbegin(), subpixels.cend(), 0,
            std::plus<int>{}, [&](Loc location) {
              return cast_single_ray(sd, location) ? 1 : 0;
            });

        return static_cast<float>(lit_subpixels) / subpixels.size();
      });
}
