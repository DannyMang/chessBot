from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "chess_engine",
        [
            "magicmoves.c",           # Add the magic moves implementation
            "bitboard.cpp",
            "python_bindings.cpp"
        ],
        cxx_std=17,
        define_macros=[("MINIMIZE_MAGIC", None)],  # Use compact magic tables
    ),
]

setup(
    name="chess_engine",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)