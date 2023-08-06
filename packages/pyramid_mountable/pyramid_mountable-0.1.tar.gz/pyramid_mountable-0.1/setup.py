#!/usr/bin/env python
import os

from setuptools import setup, find_packages

setup(name='pyramid_mountable',
      version='0.1',
      description='Provide a mountable tree to the ease creation of traversal root for pyramid',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
      ],
      author='Sherwood Wang',
      author_email='sherwood@wang.onl',
      packages=find_packages(),
      install_requires=[
          'pyramid',
          'venusian',
          'zope.interface',
          'zope.proxy',
      ]
      )
