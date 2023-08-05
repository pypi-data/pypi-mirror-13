#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

current_path = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(current_path, 'README.rst')).read()
CHANGES = open(os.path.join(current_path, 'CHANGES.rst')).read()

requires = [
    'requests',
    'python-memcached',
    'beanstalkc'
    ]

import iCrawl

setup(name='iCrawl',
      version=iCrawl.__version__,
      description='iCrawl ',
      long_description='',
      author='tasiguo',
      author_email='tasiguo@gmail.com',
      url='http://www.google.com',
      keywords='web wbs crawl',
      packages=find_packages(),
      namespace_packages=['iCrawl', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="",
      scripts=[],
      )