# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda - 
# Josie Esteban Rodriguez Condia - 
# Filippo Carlone -
# Gabriele Belli - 
#

from setuptools import setup

setup(
    name="polaris-scan",
    version="1.0.0",
    py_modules=["polaris", "chain", "constants", "log", "lib2flipflop", "parser", "profiling"],
    entry_points={
        "console_scripts": [
            "polaris=polaris:main",
        ]
    },
)