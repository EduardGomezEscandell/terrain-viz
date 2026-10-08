#include <utility>

/**
 * Returns the altitude, azimuth describing the position of the sun in the sky
 * at a certain location at a certain time Arguments:
 * - latitude, longitude
 * - seconds_since_epoch: timestamp in seconds since 1970-01-01 00:00:00 UTC
 * Output:
 * - altitude: the vertical angle between the Sun and the horizon
 * - azimuth: angle between the Sun's projection on the horizon and
 * north, clockwise
 *
 * Both input and output angles in degrees
 */
[[nodiscard]]
std::pair<float, float> sun_position(float latitude, float longitude,
                                     long seconds_since_epoch);