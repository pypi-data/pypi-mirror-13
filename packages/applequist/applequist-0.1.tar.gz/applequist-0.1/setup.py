#from distutils.core import setup
#from distutils.extension import Extension

from Cython.Distutils import build_ext

from setuptools import setup, Extension

import numpy

ext_module = Extension(
        "applequist.optimized_func",
        ["applequist/optimized_func.pyx"],
        extra_compile_args = ["-O3", "-ffast-math", "-march=native",'-fopenmp', ],
        extra_link_args = ['-fopenmp'], 
        include_dirs = [ numpy.get_include()],
        )

setup(name = "applequist",
    version = "0.1",
    packages = [ "applequist" ],
    ext_modules = [ext_module],
    cmdclass = { 'build_ext' : build_ext },
    #install_requires = [ 'numpy>=1.9.2', 'cython>=0.20.1' ],
    license = 'GPL',
    author = 'Olav Vahtras',
    maintainer = 'Ignat Harczuk',
    maintainer_email = 'ignathe@gmail.com',

)
