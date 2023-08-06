#!/usr/bin/env python
"""
Export to TIFF file format
"""

# Standard library modules.
import os

# Third party modules.
import tifffile

# Local modules.
from pyhmsa.fileformat.exporter.exporter import _Exporter, _ExporterThread
from pyhmsa.spec.condition.acquisition import AcquisitionRasterXY
from pyhmsa.spec.datum.analysislist import AnalysisList2D
from pyhmsa.spec.datum.imageraster import ImageRaster2D, ImageRaster2DSpectral
from pyhmsa.type.numerical import convert_unit

# Globals and constants variables.
_INCH_TO_MM = 25.4

class _BaseExporterTIFFThread(_ExporterThread):

    @classmethod
    def find_data(cls, datafile):
        return set(datafile.data.findkeys(AnalysisList2D)) | \
                set(datafile.data.findkeys(ImageRaster2D)) | \
                set(datafile.data.findkeys(ImageRaster2DSpectral))

    def __init__(self, datafile, dirpath, compress=0, *args, **kwargs):
        _ExporterThread.__init__(self, datafile, dirpath, compress,
                                 *args, **kwargs)

    def _calculate_resolution(self, datum):
        acqs = datum.conditions.findvalues(AcquisitionRasterXY)
        if not acqs:
            return None

        acq = next(iter(acqs)) # Take first one
        dx_in = float(convert_unit('mm', acq.step_size_x)) / _INCH_TO_MM
        dy_in = float(convert_unit('mm', acq.step_size_y)) / _INCH_TO_MM
        return (1.0 / dx_in, 1.0 / dy_in)

    def _create_tiff_writer(self, filepath):
        return tifffile.TiffWriter(filepath, bigtiff=True, software='pyHMSA')

    def _run(self, datafile, dirpath, compress, *args, **kwargs):
        raise NotImplementedError

class _ExporterTIFFThread(_BaseExporterTIFFThread):

    def _run(self, datafile, dirpath, compress, *args, **kwargs):
        basefilename = datafile.header.title or 'Untitled'

        identifiers = self.find_data(datafile)
        length = len(identifiers)
        filepaths = []

        for i, identifier in enumerate(identifiers):
            datum = datafile.data[identifier]

            self._update_status(i / length, 'Exporting %s' % identifier)

            filename = basefilename + '_' + identifier
            filepath = os.path.join(dirpath, filename + '.tif')
            self._save(filepath, datum, compress)

            filepaths.append(filepath)

        return filepaths

    def _save(self, filepath, datum, compress):
        resolution = self._calculate_resolution(datum)
        with self._create_tiff_writer(filepath) as writer:
            writer.save(datum.T, resolution=resolution, compress=compress)

class _ExporterTIFFMultiPageThread(_BaseExporterTIFFThread):

    def _run(self, datafile, dirpath, compress, *args, **kwargs):
        identifiers = self.find_data(datafile)
        length = len(identifiers)

        filename = datafile.header.title or 'Untitled'
        filepath = os.path.join(dirpath, filename + '.tif')

        with self._create_tiff_writer(filepath) as writer:
            for i, identifier in enumerate(identifiers):
                datum = datafile.data[identifier]

                self._update_status(i / length, 'Exporting %s' % identifier)

                resolution = self._calculate_resolution(datum)
                writer.save(datum.T, resolution=resolution, compress=compress)

        return [filepath]

class _BaseExporterTIFF(_Exporter):

    def __init__(self, compress=0):
        _Exporter.__init__(self)
        self._compress = compress

    def validate(self, datafile):
        _Exporter.validate(self, datafile)

        identifiers = _BaseExporterTIFFThread.find_data(datafile)
        if not identifiers:
            raise ValueError('Datafile must contain at least one ' + \
                             'AnalysisList2D, ImageRaster2D or ' + \
                             'ImageRaster2DSpectral datum')

class ExporterTIFF(_BaseExporterTIFF):

    def _create_thread(self, datafile, dirpath, *args, **kwargs):
        return _ExporterTIFFThread(datafile, dirpath, self._compress)

class ExporterTIFFMultiPage(_BaseExporterTIFF):

    def _create_thread(self, datafile, dirpath, *args, **kwargs):
        return _ExporterTIFFMultiPageThread(datafile, dirpath, self._compress)
