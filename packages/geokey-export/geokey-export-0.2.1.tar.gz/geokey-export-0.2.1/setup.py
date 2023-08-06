#!/usr/bin/env python

from os.path import join
from setuptools import setup, find_packages


name = 'geokey-export'
version = __import__(name.replace('-', '_')).__version__
repository = join('https://github.com/ExCiteS', name)

setup(
    name=name,
    version=version,
    description='Export data from GeoKey to KML or GeoJSON',
    url=repository,
    download_url=join(repository, 'tarball', version),
    author='Patrick Rickles',
    author_email='p.rickles@ucl.ac.uk',
    license='MIT',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
)
