#!/usr/bin/env python
from setuptools import setup

setup(name='pymtt',
      version='0.1.7',
      description='Command-line Text Transformer',
      long_description=open('README.rst').read(),
      author='Pavel Klemenkov',
      author_email='pklemenkov@gmail.com',
      url='https://github.com/pklemenkov/pymtt',
      download_url='https://github.com/pklemenkov/pymtt/tarball/master',
      license='GPL',
      packages=['pymtt', 'pymtt.filters'],
      install_requires=[
          'Jinja2 >=2.3'
      ],
      scripts=[
          'bin/pymtt'
      ],
      package_data={
          'pymtt.filters': ['plist', 'BSD.local.dist']
      },
      include_package_data=True
      )
