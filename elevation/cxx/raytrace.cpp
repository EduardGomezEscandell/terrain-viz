#include <pybind11/pybind11.h>

namespace py = pybind11;

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(raytrace, m, py::mod_gil_not_used()) {
    m.doc() = "pybind11 raytrace plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}