from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "chess_engine",
        [
            "chess_helpers/bitboard.cpp",
        ],
        # Example: passing in the version to the compiled code
        define_macros=[("VERSION_INFO", '"dev"')],
        cxx_std=14,
    ),
]

setup(
    name="chess_engine",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
) 