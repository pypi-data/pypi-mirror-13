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
import tempfile
import shutil

# Third party modules.
import numpy as np

# Local modules.
from pyhmsa.datafile import DataFile
from pyhmsa.spec.condition.acquisition import AcquisitionRasterXY
from pyhmsa.spec.datum.imageraster import ImageRaster2D
from pyhmsa.type.numerical import _SUPPORTED_DTYPES
from pyhmsa_matlab.fileformat.exporter.matlab import ExporterMATLAB

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

class TestExporterMATLAB(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.exp = ExporterMATLAB()

        self.datafile = _create_datafile()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        self.exp.export(self.datafile, self.tmpdir)
        filepaths = self.exp.get()

        self.assertEqual(len(filepaths), 1)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
