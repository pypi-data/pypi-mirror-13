#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages
from os import path
from version import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='mpijobs',
      version=__version__,
      py_modules=['mpijobs', 'version'],
      install_requires=['mpi4py'],
      author='Maurizio Tomasi',
      author_email='ziotom78@gmail.com',
      description='Run many jobs using MPI processes through a master/slave approach',
      long_description=long_description,
      license='MIT',
      keywords='mpi master/slave',
      url='https://github.com/ziotom78/mpijobs',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3 :: Only',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Topic :: Software Development',
          'Topic :: System :: Distributed Computing'])
