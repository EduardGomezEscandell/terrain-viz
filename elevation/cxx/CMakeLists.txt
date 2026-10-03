pybind11_add_module(raytrace bindings.cpp raytrace.cpp)
target_link_libraries(raytrace PRIVATE TBB::tbb)
install(TARGETS raytrace DESTINATION elevation)