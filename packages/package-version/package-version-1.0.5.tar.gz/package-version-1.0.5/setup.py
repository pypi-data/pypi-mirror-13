#!/usr/bin/env python
from setuptools import setup, find_packages


def version():
    import os
    v = os.getenv('PYTHON_PACKAGE_VERSION')
    if v is None:
        try:
            from package_version import PackageVersion
            pv = PackageVersion()
            v = pv.generate_next_stable(package_name='package-version')
        except ImportError:
            v = '0.0.1'
    return v

setup(name='package-version',
      version=version(),
      description='Library to generate python package version for CI',
      author='Jon Skarpeteig',
      author_email='jon.skarpeteig@gmail.com',
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      url='https://github.com/Yuav/python-package-version',
      packages=find_packages(),
      install_requires=[
          'future',
          'semantic_version',
          'flexmock'
      ],
      setup_requires=[
          'package_version'
      ],
      tests_require = [
          'future'
      ]
      )
