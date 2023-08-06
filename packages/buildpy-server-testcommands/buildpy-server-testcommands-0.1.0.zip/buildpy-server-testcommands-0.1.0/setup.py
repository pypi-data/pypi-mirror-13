#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os.path
from glob import glob

from setuptools import find_packages, setup


here = os.path.abspath('.')
README = io.open(os.path.join(here, 'README.rst')).read()

install_requires = [
    'py>=1.4.31',
    'pluggy>=0.3.1',
    'pytest>=2.8.5',
]


here = os.path.abspath('.')

setup(
    name='buildpy-server-testcommands',
    version='0.1.0',
    author='Maik Figura',
    author_email='maiksensi@gmail.com',
    maintainer='Maik Figura',
    maintainer_email='maiksensi@gmail.com',
    license='MIT',
    url='https://github.com/buildpy/buildpy-server-testcommands',
    description='buildpy-server-testcommands: Testcommand Plugin',
    long_description=README,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0]
        for path in glob('src/*.py')
    ],
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'buildpy_server':
        ["buildpy-server-testcommands = buildpy_server_testcommands.plugin"],
    },
)
