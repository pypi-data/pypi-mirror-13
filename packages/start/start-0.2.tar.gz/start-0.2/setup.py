#!/usr/bin/env python
from setuptools import setup
import start


setup(
    name='start',
    version=start.__version__,
    description='Very simple command to start a single process from a Procfile',
    author='Divio AG',
    author_email='aldryn@divio.ch',
    url='https://github.com/aldryncore/start',
    license='BSD',
    platforms=['OS Independent'],
    py_modules=['start'],
    install_requires=[
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points="""
    [console_scripts]
    start = start:cli
    """,
)
