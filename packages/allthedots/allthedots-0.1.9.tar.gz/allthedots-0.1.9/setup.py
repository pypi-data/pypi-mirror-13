#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="allthedots",
      version="0.1.9",
      author="Christian Jurke",
      author_email="christian.jurke@gmail.com",
      description="Make a list of important stuff.",
      url="https://github.com/cjrk/AllTheDots",

      py_modules = ['allthedots'],
      entry_points={
          'console_scripts':
            ['atd = allthedots:main']
      },
      install_requires=['setuptools']
)
