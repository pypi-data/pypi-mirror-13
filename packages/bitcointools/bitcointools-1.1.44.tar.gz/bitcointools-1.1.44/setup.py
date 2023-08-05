#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='bitcointools',
      version='1.1.44',
      description='Python Bitcoin Tools',
      author='Vitalik Buterin',
      author_email='vbuterin@gmail.com',
      url='http://github.com/vbuterin/pybitcointools',
      packages=['bitcointools'],
      scripts=['pybtctool'],
      include_package_data=True,
      data_files=[("bitcointools", ["bitcointools/english.txt"])],
      )
