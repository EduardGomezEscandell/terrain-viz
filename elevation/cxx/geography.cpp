#include "geography.hpp"
#include <cmath>
#include <numbers>
#include <utility>

// Used for intermediate calculations
using Float = double;

constexpr Float deg2rad(const Float deg) {
  return deg * std::numbers::pi_v<Float> / 180;
}
constexpr Float rad2deg(const Float rad) {
  return rad * 180 / std::numbers::pi_v<Float>;
}

template <unsigned int z> constexpr Float fpow(const Float x) {
  if constexpr (z == 0) {
    return 1;
  }
  // Cheap trick to avoid underflow stack unrolling at compile-time
  constexpr auto next = z == 0 ? 0 : z - 1;
  return x * fpow<next>(x);
}

namespace WGS84 {
// Semimajor axis
constexpr Float a = 6378137;

// Flattening
constexpr Float f = 1 / 298.257222101;

// Eccentricity (squared)
constexpr Float e2 = 2 * f - (f * f);

// Second eccentricity (squared)
constexpr Float eprime2 = e2 / (1 - e2);

constexpr Float n = f / (2 - f);

// Ellipsoid expansion coefficients
constexpr Float J[4] = {
    3 * n / 2 - 27 * n * n * n / 32,
    21 * n *n / 16 - 55 * n *n *n *n / 32,
    151 * n *n *n / 96,
    1097 * n *n *n *n / 512,
};

// Rectifying meridian
const Float r1 = a / (1 + n) * (1 + n * n / 4 + n * n * n * n / 64);
} // namespace WGS84

namespace UTM31N {
// Scale at meridian
constexpr Float k0 = 0.9996;

// Central meridian
constexpr Float lambda0 = deg2rad(3);

// False easting
constexpr Float FE = 500e3;

// False northing
constexpr Float FN = 0;
} // namespace UTM31N

std::pair<float, float> project_EPSG25831_to_latlon(float N, float E) {
  const Float x = E - UTM31N::FE;
  const Float y = N - UTM31N::FN;

  // Arclength accross meridian
  const Float M = y / UTM31N::k0;

  // Footprint latitude
  const Float phi1 = [M]() {
    using std::sin, WGS84::J;
    const auto mu = M / WGS84::r1;
    return mu + J[0] * sin(2 * mu) + J[1] * sin(4 * mu) + J[2] * sin(6 * mu) +
           J[3] * sin(8 * mu);
  }();

  // Radius of curvature in the prime vertical
  const Float denom = 1 - WGS84::e2 * fpow<2>(std::sin(phi1));
  const Float N1 = WGS84::a / std::sqrt(denom);

  // Radius of curvature in the prime meridian
  const Float R1 = WGS84::a * (1 - WGS84::e2) / std::pow(denom, 1.5);

  // Geometric scaling factor
  const Float D = x / (N1 * UTM31N::k0);

  // Latitude
  const Float cosP = std::cos(phi1);
  const Float cos2P = cosP * cosP;
  const Float tanP = std::tan(phi1);
  const Float tan2P = tanP * tanP;

  const Float lat =
      phi1 - (N1 * tanP) / R1 *
                 (fpow<2>(D) / 2 -
                  fpow<4>(D) / 24 *
                      (5 + 3 * tan2P + 10 * WGS84::eprime2 * cos2P -
                       4 * WGS84::eprime2 * WGS84::eprime2 * cos2P * cos2P));

  const Float lon =
      UTM31N::lambda0 +
      1 / cosP *
          (D - fpow<3>(D) / 6 * (1 + 2 * tan2P + WGS84::eprime2 * cos2P) +
           fpow<5>(D) / 120 * (5 + 28 * tan2P + 24 * tan2P * tan2P));

  return {static_cast<float>(rad2deg(lat)), static_cast<float>(rad2deg(lon))};
}
