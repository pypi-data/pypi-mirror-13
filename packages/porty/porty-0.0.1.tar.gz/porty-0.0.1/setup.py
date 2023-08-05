# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='porty',
      packages=['porty'],
      version='0.0.1',
      description='Get a free port from a specified range',
      author='André Gaul',
      author_email='andre@gaul.io',
      url='https://github.com/andrenarchy/porty',
      scripts=['scripts/porty'],
      classifiers=[
          'Intended Audience :: System Administrators',
          'Topic :: System :: Systems Administration',
          'Topic :: System :: Networking'
          ]
      )
