#!/usr/bin/env python
"""
Export to MATLAB .mat file format
"""

# Standard library modules.
import os
import re

# Third party modules.
import scipy.io.matlab

# Local modules.
from pyhmsa.fileformat.exporter.exporter import _Exporter, _ExporterThread
from pyhmsa.spec.datum.analysislist import AnalysisList2D
from pyhmsa.spec.datum.imageraster import ImageRaster2D, ImageRaster2DSpectral

# Globals and constants variables.

class _ExporterMATLABThread(_ExporterThread):

    @classmethod
    def find_data(cls, datafile):
        return set(datafile.data.findkeys(AnalysisList2D)) | \
                set(datafile.data.findkeys(ImageRaster2D)) | \
                set(datafile.data.findkeys(ImageRaster2DSpectral))

    def __init__(self, datafile, dirpath, *args, **kwargs):
        _ExporterThread.__init__(self, datafile, dirpath, *args, **kwargs)

    def _run(self, datafile, dirpath, *args, **kwargs):
        identifiers = self.find_data(datafile)
        length = len(identifiers)

        filename = datafile.header.title or 'Untitled'
        filepath = os.path.join(dirpath, filename + '.mat')

        mdict = {}
        for i, identifier in enumerate(identifiers):
            datum = datafile.data[identifier]

            self._update_status(i / length, 'Exporting %s' % identifier)

            matidentifier = re.sub('\W', '_', identifier)
            if not matidentifier[0].isalpha(): 'a' + matidentifier

            mdict[matidentifier] = datum

        scipy.io.matlab.savemat(filepath, mdict, do_compression=True)

        return [filepath]

    def _save(self, filepath, datum, compress):
        resolution = self._calculate_resolution(datum)
        with self._create_tiff_writer(filepath) as writer:
            writer.save(datum.T, resolution=resolution, compress=compress)

class ExporterMATLAB(_Exporter):

    def __init__(self):
        _Exporter.__init__(self)

    def validate(self, datafile):
        _Exporter.validate(self, datafile)

        identifiers = _ExporterMATLABThread.find_data(datafile)
        if not identifiers:
            raise ValueError('Datafile must contain at least one ' + \
                             'AnalysisList2D, ImageRaster2D or ' + \
                             'ImageRaster2DSpectral datum')

    def _create_thread(self, datafile, dirpath, *args, **kwargs):
        return _ExporterMATLABThread(datafile, dirpath)

