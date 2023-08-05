#!/usr/bin/env python
from setuptools import setup

# PyPi requires reStructuredText instead of Markdown,
# so we convert our Markdown README for the long description
try:
   import pypandoc
   long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   long_description = open('README.md').read()

# Command-line tools
entry_points = {'console_scripts': [
    'K2ephem = K2ephem:K2ephem_main'
]}

setup(name='K2ephem',
      version='1.1.0',
      description="Check if a Solar System object is "
                  "(or was) observable by NASA's K2 mission. "
                  "This command will query JPL/Horizons "
                  "to find out.",
      long_description=long_description,
      author='Geert Barentsen',
      author_email='hello@geert.io',
      url='https://github.com/KeplerGO/K2ephem',
      packages=['K2ephem'],
      install_requires=["pandas>=0.16", "K2fov>=3.0"],
      entry_points=entry_points,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
      )
