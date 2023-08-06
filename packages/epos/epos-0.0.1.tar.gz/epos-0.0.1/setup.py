#!/usr/bin/env python

from os.path import exists

from setuptools import setup

setup(name='epos',
      version='0.0.1',
      description='DAG Task scheduler and DSL on top of Mesos',
      url='http://github.com/kszucs/epos',
      maintainer='Krisztian Szucs',
      maintainer_email='szucs.krisztian@gmail.com',
      license='BSD',
      keywords='task-scheduling parallelism mesos spark',
      packages=['epos'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
