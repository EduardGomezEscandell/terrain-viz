#include <utility>

/**
 * Converts N, E coordinates from a EPSG:25831 format to the WGS 84 latitude / longitude we all know and love
 */
[[nodiscard]]
std::pair<float, float> project_EPSG25831_to_latlon(float N, float E);