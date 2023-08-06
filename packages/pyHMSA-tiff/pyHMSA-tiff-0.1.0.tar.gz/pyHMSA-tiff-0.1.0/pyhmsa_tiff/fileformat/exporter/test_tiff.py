#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2015 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil

# Third party modules.
import numpy as np

import tifffile

# Local modules.
from pyhmsa.datafile import DataFile
from pyhmsa.spec.condition.acquisition import AcquisitionRasterXY
from pyhmsa.spec.datum.imageraster import ImageRaster2D
from pyhmsa.type.numerical import _SUPPORTED_DTYPES
from pyhmsa_tiff.fileformat.exporter.tiff import ExporterTIFF, ExporterTIFFMultiPage

# Globals and constants variables.

def _create_datafile():
    datafile = DataFile()

    acq = AcquisitionRasterXY(60, 50, (0.1, 'nm'), (0.1, 'nm'))

    for dtype in _SUPPORTED_DTYPES:
        datum = ImageRaster2D(60, 50, dtype=dtype)
        datum[:] = np.random.random((60, 50)) * 255
        datum.conditions.add('Acq', acq)
        datafile.data.add(dtype.name, datum)

    return datafile

class TestExporterTIFF(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.exp = ExporterTIFF(compress=9)

        self.datafile = _create_datafile()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        self.exp.export(self.datafile, self.tmpdir)
        filepaths = self.exp.get()

        self.assertEqual(len(filepaths), len(_SUPPORTED_DTYPES))

        for filepath in filepaths:
            with tifffile.TiffFile(filepath) as tif:
                actual = tif.asarray()

            identifier = os.path.splitext(os.path.basename(filepath))[0].split('_')[1]
            expected = self.datafile.data[identifier]

            np.testing.assert_almost_equal(actual, expected.T, 4)

class TestExporterTIFFMultiPage(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.exp = ExporterTIFFMultiPage(compress=9)

        self.datafile = _create_datafile()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        self.exp.export(self.datafile, self.tmpdir)
        filepaths = self.exp.get()

        self.assertEqual(len(filepaths), 1)

        with tifffile.TiffFile(filepaths[0]) as tif:
            self.assertEqual(len(tif), len(_SUPPORTED_DTYPES))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
