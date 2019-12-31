# -*- coding: utf-8 -*-

import os
import copy
import shutil
import pathlib
import tempfile
import unittest

import numpy as np
from numpy import testing as npt

import geomodels
from geomodels import wmmf


DATAPATH = pathlib.Path(geomodels.MagneticFieldModel.default_magnetic_path())


class MetaDataTestMixin:
    def test_fields(self):
        for name in ('Name', 'Description', 'URL', 'Publisher', 'ReleaseDate',
                     'DataCutOff', 'ConversionDate', 'ID'):
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.metadata, name))
                self.assertIsInstance(getattr(self.metadata, name), str)

        for name in ('FORMAT_VERSION', 'NumModels', 'Epoch',
                     'DeltaEpoch', 'MinTime', 'MaxTime',
                     'DataVersion', 'Radius', 'MinHeight', 'MaxHeight'):
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.metadata, name))
                self.assertIsInstance(getattr(self.metadata, name), int)

    def test_get_id(self):
        self.assertEqual(self.metadata.get_id(), self.metadata.ID)


class EmptyMetaDataTestCase(MetaDataTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = wmmf.MetaData()

    def test_get_years(self):
        self.assertEqual(self.metadata.get_years(), [])


class MetaDataTestCase(MetaDataTestMixin, unittest.TestCase):
    METADATAFILE = DATAPATH / 'igrf12.wmm'

    def setUp(self) -> None:
        self.metadata = wmmf.MetaData()
        self.metadata.load(self.METADATAFILE)

    def test_load(self):
        self.assertEqual(self.metadata.FORMAT_VERSION, 1)
        self.assertEqual(self.metadata.Name, 'igrf12')
        self.assertEqual(self.metadata.NumModels, 24)
        self.assertEqual(self.metadata.Epoch, 1900)
        self.assertEqual(self.metadata.DeltaEpoch, 5)
        self.assertEqual(self.metadata.MinTime, 1900)
        self.assertEqual(self.metadata.MaxTime, 2020)

    def test_get_years(self):
        years = self.metadata.get_years()
        self.assertEqual(len(years), self.metadata.NumModels)
        for year in years:
            with self.subTest(year=year):
                self.assertIsInstance(year, int)

    # TODO: make this test more robust
    def test_str(self):
        with open(self.METADATAFILE) as fd:
            data = fd.read().strip()
        self.assertEqual(data, str(self.metadata).strip())

    def test_save(self):
        with tempfile.TemporaryDirectory() as outpath:
            filename = pathlib.Path(outpath) / 'igrf12.wmm'
            self.metadata.save(filename)
            self.assertTrue(os.path.exists(filename))

            local_metadata = wmmf.MetaData()
            local_metadata.load(filename)
            self.assertEqual(self.metadata, local_metadata)


class MetaDataFromTxtHeaderTestCase(MetaDataTestMixin, unittest.TestCase):
    COEFFFILE = pathlib.Path(__file__).parent / 'data' / 'igrf12coeffs.txt'

    def setUp(self) -> None:
        with open(self.COEFFFILE) as fd:
            data = fd.read()
        header = data.splitlines(keepends=False)[3]
        self.metadata = wmmf._metadata_from_txt_header(header)
        self.metadata.Name = 'igrf12'

    def test_from_header(self):
        self.assertEqual(self.metadata.FORMAT_VERSION, 1)
        self.assertEqual(self.metadata.Name, 'igrf12')
        self.assertEqual(self.metadata.NumModels, 24)
        self.assertEqual(self.metadata.Epoch, 1900)
        self.assertEqual(self.metadata.DeltaEpoch, 5)
        self.assertEqual(self.metadata.MinTime, 1900)
        self.assertEqual(self.metadata.MaxTime, 2020)

    def test_get_years(self):
        years = self.metadata.get_years()
        self.assertEqual(len(years), self.metadata.NumModels)
        for year in years:
            with self.subTest(year=year):
                self.assertIsInstance(year, int)

    def test_get_id(self):
        self.assertEqual(self.metadata.get_id(), 'IGRF12-A')


class WmmDataTestCase(unittest.TestCase):
    METADATAFILE = DATAPATH / 'igrf12.wmm'

    def setUp(self) -> None:
        self.wmmdata = wmmf.WmmData(self.METADATAFILE)

    def test_load_metadata(self):
        metadata = wmmf.MetaData()
        metadata.load(self.METADATAFILE)
        self.assertEqual(self.wmmdata.metadata, metadata)

    def test_load_coeffs(self):
        self.assertNotEqual(self.wmmdata.coeffs, {})
        self.assertIn('rate', self.wmmdata.coeffs)
        self.assertEqual('rate', list(self.wmmdata.coeffs.keys())[-1])

    def test_load_consistency(self):
        self.assertEqual(
            len(self.wmmdata.coeffs), self.wmmdata.metadata.NumModels + 1)
        years = [
            int(item) for item in self.wmmdata.coeffs.keys() if item != 'rate'
        ]
        self.assertEqual(years, self.wmmdata.metadata.get_years())

    def test_coeffs_data(self):
        coeffs = self.wmmdata.coeffs
        for year, sph_coeff_set in coeffs.items():
            with self.subTest(year=year):
                self.assertIsInstance(year, str)
                self.assertEqual(sph_coeff_set.C.dtype, np.dtype('<f8'))
                self.assertEqual(sph_coeff_set.S.dtype, np.dtype('<f8'))
                self.assertEqual(sph_coeff_set.C.shape, sph_coeff_set.S.shape)

    def test_save_to_dir(self):
        with tempfile.TemporaryDirectory() as outpath:
            outpath = pathlib.Path(outpath)
            metadata_filename = outpath / 'igrf12.wmm'
            bin_filename = metadata_filename.with_suffix('.wmm.cof')

            self.assertFalse(metadata_filename.is_file())
            self.assertFalse(bin_filename.is_file())

            self.wmmdata.save(outpath)

            self.assertTrue(metadata_filename.is_file())
            self.assertTrue(bin_filename.is_file())

    def test_save_to_file(self):
        with tempfile.TemporaryDirectory() as outpath:
            outpath = pathlib.Path(outpath)
            metadata_filename = outpath / 'custom_igrf12.wmm'
            bin_filename = metadata_filename.with_suffix('.wmm.cof')

            self.assertFalse(metadata_filename.is_file())
            self.assertFalse(bin_filename.is_file())

            self.wmmdata.save(metadata_filename)

            self.assertTrue(metadata_filename.is_file())
            self.assertTrue(bin_filename.is_file())

    def test_from_metadata_and_coeffs(self):
        src_wmmdata = self.wmmdata
        dst_wmmdata = wmmf.WmmData.from_metadata_and_coeffs(
            src_wmmdata.metadata, src_wmmdata.coeffs)
        self.assertEqual(src_wmmdata.metadata, dst_wmmdata.metadata)
        self.assertEqual(src_wmmdata.coeffs, dst_wmmdata.coeffs)

    def test_from_inconsistent_metadata_and_coeffs_01(self):
        src_wmmdata = self.wmmdata
        metadata = copy.copy(src_wmmdata.metadata)
        metadata.NumModels = metadata.NumModels + 2
        self.assertRaises(
            RuntimeError,
            wmmf.WmmData.from_metadata_and_coeffs,
            metadata, src_wmmdata.coeffs)

    def test_from_inconsistent_metadata_and_coeffs_02(self):
        src_wmmdata = self.wmmdata
        metadata = copy.copy(src_wmmdata.metadata)
        metadata.NumModels = metadata.NumModels - 2
        self.assertRaises(
            RuntimeError,
            wmmf.WmmData.from_metadata_and_coeffs,
            metadata, src_wmmdata.coeffs)

    def test_from_inconsistent_metadata_and_coeffs_03(self):
        coeffs = self.wmmdata.coeffs.copy()
        coeffs.pop('rate')
        self.assertRaises(
            RuntimeError,
            wmmf.WmmData.from_metadata_and_coeffs,
            self.wmmdata.metadata, coeffs)

    def test_from_inconsistent_metadata_and_coeffs_04(self):
        coeffs = self.wmmdata.coeffs.copy()
        year = '1950'
        item = coeffs.pop(year)
        coeffs[year] = item
        item = coeffs.pop('rate')
        coeffs['tare'] = item
        self.assertEqual(list(coeffs.keys())[-2], year)
        self.assertRaises(
            RuntimeError,
            wmmf.WmmData.from_metadata_and_coeffs,
            self.wmmdata.metadata, coeffs)


class ImportIgrfTxtTestCase(WmmDataTestCase):
    IGRFTXT = pathlib.Path(__file__).parent / 'data' / 'igrf12coeffs.txt'

    def setUp(self) -> None:
        self.wmmdata = wmmf.import_igrf_txt(self.IGRFTXT)

    def test_load_metadata(self):
        metadata = wmmf.MetaData()
        metadata.load(self.METADATAFILE)
        for name in vars(self.wmmdata.metadata):
            with self.subTest(name=name):
                if name.startswith('_'):
                    continue
                if name in ('Description', 'ConversionDate'):
                    continue
                value = getattr(self.wmmdata.metadata, name)
                if value == 'N/A':
                    continue
                self.assertEqual(value, getattr(metadata, name))


NO_NETWORK = bool(
    os.environ.get('GEOMODELS_NO_NETWORK') in ('1', 'OK', 'TRUE', 'YES'))


@unittest.skipIf(NO_NETWORK, 'no network')
class ImportRemoteIgrfTxtTestCase(WmmDataTestCase):
    IGRFTXT = 'https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/igrf13coeffs.txt'


class DataCrossCheckTestCase(unittest.TestCase):
    METADATAFILE = DATAPATH / 'igrf12.wmm'
    IGRFTXT = pathlib.Path(__file__).parent / 'data' / 'igrf12coeffs.txt'

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()

        wmmtxt = wmmf.import_igrf_txt(self.IGRFTXT)
        wmmtxt.save(self.tmpdir)

        filename = pathlib.Path(self.tmpdir) / 'igrf12.wmm'
        self.wmmtxt = wmmf.WmmData(filename)
        self.wmmbin = wmmf.WmmData(self.METADATAFILE)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)

    def test_coeffs_keys(self):
        self.assertEqual(
            list(self.wmmbin.coeffs.keys()), list(self.wmmtxt.coeffs.keys()))

    def test_data(self):
        it = zip(
            self.wmmbin.coeffs.keys(),
            self.wmmbin.coeffs.values(),
            self.wmmtxt.coeffs.values(),
        )
        for year, bin_, txt in it:
            with self.subTest(year=year):
                self.assertEqual(bin_.C.shape, txt.C.shape)
                self.assertEqual(bin_.S.shape, txt.S.shape)
                npt.assert_allclose(bin_.C, txt.C)
                npt.assert_allclose(bin_.S, txt.S)

    def test_bin_filesize(self):
        orig = pathlib.Path(self.METADATAFILE).with_suffix('.wmm.cof')
        new = pathlib.Path(self.tmpdir) / 'igrf12.wmm.cof'
        self.assertEqual(orig.stat().st_size, new.stat().st_size)

    def test_binary_data(self):
        orig = pathlib.Path(self.METADATAFILE).with_suffix('.wmm.cof')
        new = pathlib.Path(self.tmpdir) / 'igrf12.wmm.cof'
        self.assertEqual(orig.read_bytes(), new.read_bytes())


if __name__ == '__main__':
    unittest.main()
