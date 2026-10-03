pybind11_add_module(raytrace bindings.cpp raytrace.cpp)
install(TARGETS raytrace DESTINATION elevation)