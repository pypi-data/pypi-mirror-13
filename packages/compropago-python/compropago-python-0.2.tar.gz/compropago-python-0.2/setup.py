
"""Python package for the ComproPago API
See:
https://github.com/tzicatl/compropago-python
"""
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README.rst file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name = 'compropago-python',
    version = '0.2',
    description = 'Python library for ComproPago',
    long_description = long_description,
    url = 'http://github.io/tzicatl/compropago-python',
    author = 'Noe Nieto',
    author_email = 'nnieto@noenieto.com',
    packages = find_packages(),
    license = 'MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='ecommerce e-commerce payment development mexico',
    install_requires = ['requests',],
    extras_require ={
        'dev': ['nose>=1.0', 'responses'],
    }
)
