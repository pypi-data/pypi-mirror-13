#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pils',
          version = '0.1.23-33',
          description = '''PILS - Python uTILS''',
          long_description = '''PILS is a container for utilities written in python''',
          author = "",
          author_email = "",
          license = 'Apache License 2.0',
          url = 'https://github.com/ImmobilienScout24/pils',
          scripts = [],
          packages = ['pils'],
          py_modules = [],
          classifiers = ['Development Status :: 3 - Alpha', 'Programming Language :: Python'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "boto3" ],
          
          zip_safe=True
    )
