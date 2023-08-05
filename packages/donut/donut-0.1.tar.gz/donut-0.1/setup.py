#!/usr/bin/env python

import os

from setuptools import setup

source_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(source_dir, 'donut.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[-1].strip()

long_description = open(os.path.join(source_dir, 'README.md')).read()

setup(name='donut',
      license='MIT',
      version=version,
      description='Makes symlinks to dotfiles.',
      long_description=long_description,
      author='Luke Olson',
      author_email='luke.olson@gmail.com',
      url='https://github.com/lukeolson/donut',
      py_modules=['donut'],
      entry_points={'console_scripts': ['donut = donut:main']},
      classifiers=['Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Utilities'])
