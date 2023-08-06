#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

import versioneer

# Local modules.

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyHMSA-tiff',
      version=versioneer.get_version(),
      description='',
      long_description=long_description,

      author='Philippe Pinard',
      author_email='philippe.pinard@gmail.com',

      url='http://pyhmsa.readthedocs.org',
      license='MIT',
      keywords='microscopy microanalysis hmsa file format',

      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Physics',
        ],

      packages=find_packages(),

      install_requires=['pyhmsa', 'tifffile'],
      tests_require=['nose', 'coverage', 'numpy'],

      zip_safe=True,

      test_suite='nose.collector',

      entry_points=\
        {
         'pyhmsa.fileformat.exporter':
            ['TIFF = pyhmsa_tiff.fileformat.exporter.tiff:ExporterTIFF',
             'TIFF (multi-page) = pyhmsa_tiff.fileformat.exporter.tiff:ExporterTIFFMultiPage'],
         },

      cmdclass=versioneer.get_cmdclass(),
     )
