#!/usr/bin/env python
from __future__ import with_statement
import os
from setuptools import setup

readme = 'README.md'
if os.path.exists('README.rst'):
    readme = 'README.rst'
with open(readme) as f:
    long_description = f.read()

setup(
    name='stacktracer',
    version='0.1.0',
    author='messense',
    author_email='messense@icloud.com',
    url='https://github.com/messense/stacktracer',
    keywords='stack, tracer, multi-threaded, threading',
    description='Stack tracer for multi-threaded applications',
    long_description=long_description,
    py_modules=['stacktracer'],
    install_requires=[
        'pygments',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
