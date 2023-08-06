"""Setup for pycalc
"""
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
import sys
from setuptools import setup

ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
if ON_RTD:
    __version__ = 'master'
else:
    # Hack to avoid having to import __init__.py before pycalc
    # is installed
    sys.path.insert(0, os.path.abspath('./pycalc'))
    from version import __version__
    sys.path.pop(0)


read_plain = lambda fname: open(
    os.path.join(os.path.dirname(__file__), fname), 'r').read()
try:
    from pypandoc import convert
    read_md = lambda fname: convert(fname, 'rst')
except ImportError:
    print("Warning: pypandoc module not found")
    read_md = read_plain

LONG_DESCRIPTION = 'Simple calculator based on Python libraries'
if os.path.exists('README.rst'):
    print("README.rst found...")
    LONG_DESCRIPTION = read_plain('README.rst')
elif os.path.exists('README.md'):
    print("RADME.md found, converting to rst")
    LONG_DESCRIPTION = read_md('README.md')

setup(
    name="pycalc",
    version=__version__,
    author="Peter Duerr",
    author_email="duerrp@gmail.com",
    description="Use python as a calculator...",
    license="MIT",
    keywords="science",
    url="https://github.com/duerrp/pycalc",
    packages=['pycalc'],
    scripts=['calc'],
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'apipkg',
        'lazy_object_proxy',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
