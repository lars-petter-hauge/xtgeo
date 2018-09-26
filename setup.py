#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

import numpy

from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import setup, find_packages, Extension
from distutils.command.build import build as _build
import versioneer

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
    # 'segyio',
]


class build(_build):
    # different order: build_ext *before* build_py
    sub_commands = [('build_ext', _build.has_ext_modules),
                    ('build_py', _build.has_pure_modules),
                    ('build_clib', _build.has_c_libraries),
                    ('build_scripts', _build.has_scripts)]


# get all C sources
sources = ['src/xtgeo/cxtgeo/cxtgeo.i']

# Obtain the numpy include directory. This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# cxtgeo extension module
_cxtgeo = Extension('xtgeo.cxtgeo._cxtgeo',
                    sources=sources,
                    include_dirs=['src/xtgeo/cxtgeo/clib/src', numpy_include],
                    library_dirs=['src/xtgeo/cxtgeo/clib/lib'],
                    libraries=['cxtgeo'],
                    swig_opts=['-modern'],
)



setup(
    name='xtgeo',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="XTGeo Python library for grids, surfaces, wells, etc",
    long_description=readme + '\n\n' + history,
    author="Jan C. Rivenaes",
    author_email='jriv@statoil.com',
    url='https://github.com/Statoil/xtgeo-python',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    ext_modules=[_cxtgeo],
    # packages=find_packages('xtgeo'),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='xtgeo',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
