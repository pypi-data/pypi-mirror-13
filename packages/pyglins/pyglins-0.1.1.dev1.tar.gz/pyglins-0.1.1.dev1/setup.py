# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from pyglins import __version__, __description__


def read_readme():
    with open('README.rst') as file:
        description = file.read()
    return description


setup(name='pyglins',
      version=__version__,
      description=__description__,
      long_description=read_readme(),
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          'Operating System :: OS Independent'],
      keywords='plugin manager',
      author='Javier Caballero',
      author_email='paxet83@gmail.com',
      url='https://github.com/paxet/pyglins',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      )

