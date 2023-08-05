#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
  name='gen_rst_readme',
  version='0.0.1',
  description='Generates a rst readme from a md readme.',
  long_description=open('README').read(),
  author='Christopher Su',
  author_email='gh@christopher.su',
  url='https://github.com/christophersu/gen_rst_readme',
  packages=find_packages(),
  install_requires=[
      "pyandoc==0.0.1",
      "wsgiref==0.1.2",
  ],
  entry_points={
    'console_scripts': [
      'gen_rst_readme=gen_rst_readme.gen_rst_readme:main'
    ],
  }
)
