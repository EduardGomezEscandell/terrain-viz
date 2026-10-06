#include <utility>

/**
 * Returns the elevation, azimuth describing the position of the sun in the sky
 * at a certain location at a certain time Arguments:
 * - latitude, longitude: in degrees
 * - seconds_since_epoch: timestamp in seconds since 1970-01-01 00:00:00 UTC
 * Output:
 * - elevation (in radians): the vertical angle between the Sun and the horizon
 * - azimuth (in radians): angle between the Sun's projection on the horizon and
 * north, clockwise
 */
[[nodiscard]]
std::pair<float, float> sun_position(float latitude, float longitude,
                                     long long seconds_since_epoch);