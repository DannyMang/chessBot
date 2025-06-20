#!/bin/bash
# run bash build.sh to build the C++ extension.
python3 -m pip install pybind11
python3 setup.py build_ext --inplace 