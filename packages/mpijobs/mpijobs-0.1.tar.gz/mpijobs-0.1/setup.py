#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='mpijobs',
      version='0.1',
      py_modules=['mpijobs'],
      install_requires=['mpi4py'],
      author='Maurizio Tomasi',
      author_email='ziotom78@gmail.com',
      description='Run many jobs using MPI processes through a master/slave approach',
      license='MIT',
      keywords='mpi master/slave',
      url='https://github.com/ziotom78/mpijobs')
