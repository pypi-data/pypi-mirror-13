#!/usr/bin/env python


from setuptools import setup

NAME = 'htptimeclient'
VERSION = '0.1'
LICENSE = 'BSD License'
AUTHOR = 'Markus Juenemann'
EMAIL = 'info@htptime.org'
DESCRIPTION = 'Example client of the www.htptime.org project'
URL = 'https://github.com/mjuenema/htptime'
REQUIRES = ['requests', 'ntpdshm', 'python-daemon']

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      py_modules=[NAME],
      install_requires=REQUIRES,
      license=LICENSE,
      entry_points={
          'console_scripts': [
              'htptime.py = htptimeclient:main'
          ]
      }
)
