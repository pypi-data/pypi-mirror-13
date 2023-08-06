"""ComproPago payment processor for Django-LFS
See:
https://github.com/tzicatl/lfs-compropago
"""
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()
with open(path.join(here, 'CONTRIBUTORS.rst')) as f:
    long_description += f.read()
with open(path.join(here, 'CHANGES.rst')) as f:
    long_description += f.read()


setup(
    name = 'lfs-compropago',
    version = '0.4.3',
    description = 'ComproPago payment processor for Django-LFS',
    long_description = long_description,
    url = 'http://github.io/tzicatl/lfs-compropago',
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
    keywords='ecommerce e-commerce payment development mexico lfs django-lfs',
    include_package_data=True,
    install_requires = ['compropago-python>=0.2','python-dateutil', 'suds', 'beautifulsoup4', 'lxml'],
    tests_require = ['nose>=1.0', 'responses'],
)
