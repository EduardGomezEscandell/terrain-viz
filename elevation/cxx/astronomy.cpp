#include "astronomy.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <numbers>
#include <stdexcept>

static constexpr float pi = std::numbers::pi;

[[nodiscard]]
constexpr auto deg2rad(auto deg) {
  return (2 * pi / 360) * deg;
}

[[nodiscard]]
constexpr auto rad2deg(auto deg) {
  return deg / (2 * pi / 360);
}

/**
 * Angle (in radians) the earth has advanced through its orbit since spring
 * equinox
 */
[[nodiscard]]
float year_angle(std::tm const &utctime) {
  const auto yearday =
      static_cast<float>(utctime.tm_yday * 24 * 3600 + utctime.tm_hour * 3600 +
                         utctime.tm_min * 60 + utctime.tm_sec) /
      3600.0 / 24.0;
  return 2 * pi * (yearday - 81) / 365;
}

/**
 * Angle (in radians) the earth has rotated since noon
 */
[[nodiscard]]
float day_angle(std::tm const &utctime, int timezone_offset_seconds) {
  constexpr int seconds_in_a_day = 24 * 3600;
  const int seconds_since_midnight =
      (3600 * utctime.tm_hour + 60 * utctime.tm_min + utctime.tm_sec +
       timezone_offset_seconds) %
      seconds_in_a_day;
  const int seconds_since_noon = seconds_since_midnight - 12 * 3600;

  return 2 * pi * seconds_since_noon / (24 * 3600);
}

/**
 * Empirical correction due to earth's orbit eccentricity, in seconds
 */
[[nodiscard]]
int equation_of_time(std::tm const &utctime) {
  const auto B = year_angle(utctime);
  const float eot_minutes =
      9.87 * std::sin(2 * B) - 7.53 * std::cos(B) - 1.5 * std::sin(B);
  return static_cast<int>(60 * eot_minutes);
}

/**
 * Sun elevation (angle above horizon) based on the declination d, latitude phi,
 * and day angle
 *
 * All angles in radians
 */
[[nodiscard]]
float elevation(float d, float phi, float day_angle) {
  const float x = std::sin(d) * std::sin(phi) +
                  std::cos(d) * std::cos(phi) * std::cos(day_angle);
  // Use std::clamp in case floating-point error moves x in asin(x) out side the
  // range
  return std::asin(std::clamp(x, -1.0f, 1.0f));
}

/**
 * Sun azimuth (angle from north) based pn the declination d, latitude phi,
 *  day angle, and sun elevation.
 *
 *  All angles in radians
 */
[[nodiscard]]
float azimuth(float d, float phi, float day_angle, float elevation) {
  const float x = (std::sin(d) * std::cos(phi) -
                   std::cos(d) * std::sin(phi) * std::cos(day_angle)) /
                  std::cos(elevation);

  // Use std::clamp to prevent floating point errors blowing up the computation
  const float az = std::acos(std::clamp(x, -1.0f, 1.0f));

  // acos does not know what quadrant to put the angle in
  // We must flip its sign in the afternoon
  if (day_angle > 0) {
    return 2 * std::numbers::pi - az;
  }
  return az;
}

std::pair<float, float> sun_position(float latitude, float longitude,
                                     long seconds_since_epoch) {
  // Use time and longitude to know how far along the year and the day we
  // are
  const std::tm time_utc = [=]() {
    auto *time = std::gmtime(&seconds_since_epoch);
    if (time == nullptr) {
      throw std::runtime_error("Could not parse seconds since epoch");
    }
    return *time;
  }();

  const float time_correction_seconds =
      240 * longitude + equation_of_time(time_utc);
  const float day_angle = ::day_angle(time_utc, time_correction_seconds);

  // Compute relevant magnitudes
  const float declination = deg2rad(23.45) * std::sin(year_angle(time_utc));
  const float elevation =
      ::elevation(declination, deg2rad(latitude), day_angle);
  const float azimuth =
      ::azimuth(declination, deg2rad(latitude), day_angle, elevation);

  return {rad2deg(elevation), rad2deg(azimuth)};
}