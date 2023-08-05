#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beaker-es-plot',
    version='0.0.0',

    url='https://github.com/ei-grad/beaker-es-plot',
    author='Andrew Grigorev',
    author_email='andrew@ei-grad.ru',

    description='ESPlot class for Beaker Notebook',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='elasticsearch beaker beakernotebook plots',

    py_modules=['esplot'],

    install_requires=[
        'matplotlib',
        'python-dateutil',
    ],
)
