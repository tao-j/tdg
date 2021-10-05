from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize

import numpy as np

extensions = [
    Extension(
        "decomp",
        ["decomp.pyx"],
        include_dirs=[np.get_include()],
        # language="c++",
    )
]

setup(
    ext_modules = cythonize(extensions, annotate=True)
)
