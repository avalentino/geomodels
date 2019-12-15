# -*- coding: utf-8 -*-

import os
import shutil
import pathlib
import datetime
import tempfile
import unittest

import numpy as np
from numpy import testing as npt

from geomodels import GeoidModel, EHeightConvDir
from geomodels import get_default_data_path
from geomodels.test.utils import dms_to_dec


class StaticMethodsTestCase(unittest.TestCase):
    def test_default_geoid_path(self):
        self.assertIsInstance(
            GeoidModel.default_geoid_path(), str)
        self.assertEqual(
            GeoidModel.default_geoid_path(),
            os.path.join(get_default_data_path(), 'geoids')
        )

    def test_default_geoid_name(self):
        names = (
            'egm84-30',
            'egm84-15',
            'egm96-15',
            'egm96-5',
            'egm2008-5',
            'egm2008-2_5',
            'egm2008-1',
        )
        self.assertTrue(GeoidModel.default_geoid_name() in names)


class InstantiationTestCase(unittest.TestCase):
    MODEL_NAME = 'egm96-5'

    def test_name(self):
        model = GeoidModel(self.MODEL_NAME)
        self.assertIsInstance(model, GeoidModel)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)

    def test_default_path(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)

    def test_custom_path(self):
        default_path = pathlib.Path(GeoidModel.default_geoid_path())
        with tempfile.TemporaryDirectory() as dirname:
            geoid_path = pathlib.Path(dirname) / default_path.name
            geoid_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, geoid_path)

            model = GeoidModel(self.MODEL_NAME, geoid_path)
            self.assertEqual(model.geoid_name(), self.MODEL_NAME)
            self.assertEqual(model.geoid_directory(), str(geoid_path))

    def test_custom_path_from_env01(self):
        default_path = pathlib.Path(GeoidModel.default_geoid_path())
        with tempfile.TemporaryDirectory() as dirname:
            geoid_path = pathlib.Path(dirname) / default_path.name
            geoid_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, geoid_path)

            old_env = os.environ.get('GEOGRAPHICLIB_DATA')
            os.environ['GEOGRAPHICLIB_DATA'] = dirname
            try:
                model = GeoidModel(self.MODEL_NAME)
                self.assertEqual(model.geoid_name(), self.MODEL_NAME)
                self.assertEqual(model.geoid_directory(), str(geoid_path))
            finally:
                if old_env is None:
                    del os.environ['GEOGRAPHICLIB_DATA']
                else:
                    os.environ['GEOGRAPHICLIB_DATA'] = old_env

    def test_custom_path_from_env02(self):
        default_path = pathlib.Path(GeoidModel.default_geoid_path())
        with tempfile.TemporaryDirectory() as dirname:
            geoid_path = pathlib.Path(dirname) / default_path.name
            geoid_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, geoid_path)

            old_env = os.environ.get('GEOGRAPHICLIB_GEOID_PATH')
            os.environ['GEOGRAPHICLIB_GEOID_PATH'] = str(geoid_path)
            try:
                model = GeoidModel(self.MODEL_NAME)
                self.assertEqual(model.geoid_name(), self.MODEL_NAME)
                self.assertEqual(model.geoid_directory(), str(geoid_path))
            finally:
                if old_env is None:
                    del os.environ['GEOGRAPHICLIB_GEOID_PATH']
                else:
                    os.environ['GEOGRAPHICLIB_GEOID_PATH'] = old_env

    def test_cubic_true(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, cubic=True)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertEqual(model.interpolation(), 'cubic')

    def test_cubic_false(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, cubic=False)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertEqual(model.interpolation(), 'bilinear')

    def test_threadsafe_true(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, threadsafe=True)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertTrue(model.threadsafe())

    def test_threadsafe_false(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, threadsafe=False)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertFalse(model.threadsafe())

    def test_positional_true_false(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, True, False)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertEqual(model.interpolation(), 'cubic')
        self.assertFalse(model.threadsafe())

    def test_positional_false_true(self):
        path = GeoidModel.default_geoid_path()
        model = GeoidModel(self.MODEL_NAME, path, False, True)
        self.assertEqual(model.geoid_name(), self.MODEL_NAME)
        self.assertEqual(model.geoid_directory(), path)
        self.assertEqual(model.interpolation(), 'bilinear')
        self.assertTrue(model.threadsafe())


class InfoMethodsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.name = GeoidModel.default_geoid_name()
        self.datapath = GeoidModel.default_geoid_path()
        self.model = GeoidModel(self.name, self.datapath)

    def test_description(self):
        description = self.model.description()
        self.assertIsInstance(description, str)
        self.assertNotEqual(description, 'NONE')

    def test_datetime(self):
        datestr = self.model.datetime()
        self.assertIsInstance(datestr, str)
        self.assertNotEqual(datestr, 'UNKNOWN')
        # date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        self.assertLess(date, datetime.datetime.now())

    def test_geoid_file(self):
        filename = self.model.geoid_file()
        self.assertIn(self.name, filename)
        self.assertIn(self.datapath, filename)

    def test_geoid_name(self):
        name = self.model.geoid_name()
        self.assertEqual(name, self.name)

    def test_geoid_directory(self):
        path = self.model.geoid_directory()
        self.assertEqual(path, self.datapath)

    def test_interpolation(self):
        self.assertIn(self.model.interpolation(), ['cubic', 'bilinear'])

    def test_threadsafe(self):
        self.assertIsInstance(self.model.threadsafe(), bool)

    def test_max_error(self):
        self.assertIsInstance(self.model.max_error(), float)
        self.assertGreater(self.model.max_error(), 0)

    def test_rms_error(self):
        self.assertIsInstance(self.model.rms_error(), float)
        self.assertGreater(self.model.rms_error(), 0)

    def test_max_vs_rms_error(self):
        self.assertLessEqual(self.model.rms_error(), self.model.max_error())

    def test_offset(self):
        self.assertIsInstance(self.model.offset(), float)

    def test_scale(self):
        self.assertIsInstance(self.model.scale(), float)
        self.assertGreater(self.model.scale(), 0)

    def equator_radius(self):
        self.assertIsInstance(self.model.equator_radius(), float)
        self.assertGreater(self.model.equator_radius(), 5e6)

    def test_flattening(self):
        self.assertIsInstance(self.model.flattening(), float)
        self.assertGreater(self.model.flattening(), 0)
        self.assertLess(self.model.flattening(), 1)


class CacheTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.name = GeoidModel.default_geoid_name()
        self.model = GeoidModel(self.name)

    def test_cache_clear(self):
        self.model.cache_clear()
        self.assertFalse(self.model.cache())
        self.model.cache_clear()
        self.assertFalse(self.model.cache())

    def test_cache_all(self):
        self.model.cache_clear()
        self.assertFalse(self.model.cache())
        self.model.cache_all()
        self.assertTrue(self.model.cache())
        self.assertEqual(self.model.cache_south(), -90)
        self.assertEqual(self.model.cache_west(), 0)
        self.assertEqual(self.model.cache_north(), +90)
        self.assertEqual(self.model.cache_east(), 360)
        self.model.cache_clear()

    def test_cache_area(self):
        south = -10
        west = -10
        north = 10
        east = 10

        self.model.cache_clear()
        self.assertFalse(self.model.cache())
        self.model.cache_area(south, west, north, east)
        self.assertTrue(self.model.cache())
        self.assertAlmostEqual(self.model.cache_south(), south, delta=0.1)
        self.assertAlmostEqual(self.model.cache_west(), west, delta=0.1)
        self.assertAlmostEqual(self.model.cache_north(), north, delta=0.1)
        self.assertAlmostEqual(self.model.cache_east(), east, delta=0.1)
        self.model.cache_clear()

    def test_cache(self):
        self.model.cache_clear()
        self.assertIsInstance(self.model.cache(), bool)
        self.assertFalse(self.model.cache())

    def test_cache_south(self):
        self.model.cache_all()
        self.assertIsInstance(self.model.cache_south(), float)
        self.assertAlmostEqual(self.model.cache_south(), -90)
        self.model.cache_clear()

    def test_cache_west(self):
        self.model.cache_all()
        self.assertIsInstance(self.model.cache_west(), float)
        self.assertAlmostEqual(self.model.cache_west(), 0)
        self.model.cache_clear()

    def test_cache_north(self):
        self.model.cache_all()
        self.assertIsInstance(self.model.cache_north(), float)
        self.assertAlmostEqual(self.model.cache_north(), +90)
        self.model.cache_clear()

    def test_cache_east(self):
        self.model.cache_all()
        self.assertIsInstance(self.model.cache_east(), float)
        self.assertAlmostEqual(self.model.cache_east(), 360)
        self.model.cache_clear()


class ComputationTestCase(unittest.TestCase):
    LAT = +dms_to_dec(16, 46, 33)   # 16:46:33N
    LON = -dms_to_dec(3, 0, 34)     # 03:00:34W
    HEIGHT = +28.7068               # [m]
    GHEIGHT = +300                  # [m]
    EHEIGHT = HEIGHT + GHEIGHT      # [m]

    # $ echo 16:46:33N 3:00:34W | GeoidEval
    # 28.7068
    # $ echo 16.775833333333335 -3.0094444444444446 | GeoidEval
    # 28.7068

    def setUp(self) -> None:
        self.name = GeoidModel.default_geoid_name()
        self.model = GeoidModel(self.name)

    def test_compute_scalar(self):
        h = self.model(self.LAT, self.LON)
        npt.assert_allclose(h, self.HEIGHT)

    def test_geoid_to_ellipsoid_scalar(self):
        dir_ = EHeightConvDir.GEOIDTOELLIPSOID
        h = self.model.convert_height(self.LAT, self.LON, self.GHEIGHT, dir_)
        npt.assert_allclose(h, self.EHEIGHT)

    def test_ellipsoid_to_geoid_scalar(self):
        dir_ = EHeightConvDir.ELLIPSOIDTOGEOID
        h = self.model.convert_height(self.LAT, self.LON, self.EHEIGHT, dir_)
        npt.assert_allclose(h, self.GHEIGHT)

    def test_convert_height_dir_none(self):
        dir_ = EHeightConvDir.NONE
        h = self.model.convert_height(self.LON, self.LAT, self.EHEIGHT, dir_)
        npt.assert_allclose(h, self.EHEIGHT)


class VectorComputationTestCase(unittest.TestCase):
    LAT = np.asarray([
        [+dms_to_dec(16, 46, 33), -dms_to_dec(16, 46, 43)],
        [-dms_to_dec(16, 56, 33), +dms_to_dec(16, 56, 43)],
    ])
    LON = np.asarray([
        [-dms_to_dec(3, 0, 34), +dms_to_dec(3, 0, 44)],
        [+dms_to_dec(3, 10, 34), -dms_to_dec(3, 10, 44)],
    ])
    HEIGHT = np.asarray([
        [+28.7068, +14.8866],
        [+15.0314, +28.6599],
    ])
    GHEIGHT = np.asarray([
        [+300, +400000],
        [+400000, +300],
    ])
    EHEIGHT = HEIGHT + GHEIGHT
    RTOL = 2.5e-6

    def setUp(self) -> None:
        self.name = GeoidModel.default_geoid_name()
        self.model = GeoidModel(self.name)

    def test_compute_vector(self):
        h = self.model(self.LAT.flatten(), self.LON.flatten())
        npt.assert_allclose(h, self.HEIGHT.flatten(), rtol=self.RTOL)

    def test_compute_matrix(self):
        h = self.model(self.LAT, self.LON)
        npt.assert_allclose(h, self.HEIGHT, rtol=self.RTOL)

    def test_geoid_to_ellipsoid_vector(self):
        dir_ = EHeightConvDir.GEOIDTOELLIPSOID
        h = self.model.convert_height(
            self.LAT.flatten(), self.LON.flatten(), self.GHEIGHT.flatten(),
            dir_)
        npt.assert_allclose(h, self.EHEIGHT.flatten(), rtol=self.RTOL)

    def test_geoid_to_ellipsoid_matrix(self):
        dir_ = EHeightConvDir.GEOIDTOELLIPSOID
        h = self.model.convert_height(self.LAT, self.LON, self.GHEIGHT, dir_)
        npt.assert_allclose(h, self.EHEIGHT, rtol=self.RTOL)

    def test_ellipsoid_to_geoid_vector(self):
        dir_ = EHeightConvDir.ELLIPSOIDTOGEOID
        h = self.model.convert_height(
            self.LAT.flatten(), self.LON.flatten(), self.EHEIGHT.flatten(),
            dir_)
        npt.assert_allclose(h, self.GHEIGHT.flatten(), rtol=self.RTOL)

    def test_ellipsoid_to_geoid_matrix(self):
        dir_ = EHeightConvDir.ELLIPSOIDTOGEOID
        h = self.model.convert_height(self.LAT, self.LON, self.EHEIGHT, dir_)
        npt.assert_allclose(h, self.GHEIGHT, rtol=self.RTOL)

    def test_convert_height_dir_none_vector(self):
        dir_ = EHeightConvDir.NONE
        h = self.model.convert_height(
            self.LON.flatten(), self.LAT.flatten(), self.EHEIGHT.flatten(),
            dir_)
        npt.assert_allclose(h, self.EHEIGHT.flatten())

    def test_convert_height_dir_none_matrix(self):
        dir_ = EHeightConvDir.NONE
        h = self.model.convert_height(self.LON, self.LAT, self.EHEIGHT, dir_)
        npt.assert_allclose(h, self.EHEIGHT)


class ConstHeightVectorComputationTestCase(unittest.TestCase):
    LAT = np.asarray([
        [+dms_to_dec(16, 46, 33), +dms_to_dec(16, 56, 43)],
        [+dms_to_dec(16, 46, 33), +dms_to_dec(16, 56, 43)],
    ])
    LON = np.asarray([
        [-dms_to_dec(3, 0, 34), -dms_to_dec(3, 10, 44)],
        [-dms_to_dec(3, 0, 34), -dms_to_dec(3, 10, 44)],
    ])
    HEIGHT = np.asarray([
        [+28.7068, +28.6599],
        [+28.7068, +28.6599],
    ])
    KHEIGHT = +300
    RTOL = 2.5e-6

    def setUp(self) -> None:
        self.name = GeoidModel.default_geoid_name()
        self.model = GeoidModel(self.name)

    def test_geoid_to_ellipsoid_vector(self):
        dir_ = EHeightConvDir.GEOIDTOELLIPSOID
        h = self.model.convert_height(
            self.LAT.flatten(), self.LON.flatten(), self.KHEIGHT, dir_)
        eheight = self.HEIGHT + self.KHEIGHT
        npt.assert_allclose(h, eheight.flatten(), rtol=self.RTOL)

    def test_geoid_to_ellipsoid_matrix(self):
        dir_ = EHeightConvDir.GEOIDTOELLIPSOID
        h = self.model.convert_height(self.LAT, self.LON, self.KHEIGHT, dir_)
        eheight = self.HEIGHT + self.KHEIGHT
        npt.assert_allclose(h, eheight, rtol=self.RTOL)

    def test_ellipsoid_to_geoid_vector(self):
        dir_ = EHeightConvDir.ELLIPSOIDTOGEOID
        h = self.model.convert_height(
            self.LAT.flatten(), self.LON.flatten(), self.KHEIGHT, dir_)
        gheight = self.KHEIGHT - self.HEIGHT
        npt.assert_allclose(h, gheight.flatten(), rtol=self.RTOL)

    def test_ellipsoid_to_geoid_matrix(self):
        dir_ = EHeightConvDir.ELLIPSOIDTOGEOID
        h = self.model.convert_height(self.LAT, self.LON, self.KHEIGHT, dir_)
        gheight = self.KHEIGHT - self.HEIGHT
        npt.assert_allclose(h, gheight, rtol=self.RTOL)

    def test_convert_height_dir_none_vector(self):
        dir_ = EHeightConvDir.NONE
        h = self.model.convert_height(
            self.LON.flatten(), self.LAT.flatten(), self.KHEIGHT, dir_)
        npt.assert_allclose(h, np.full_like(h, self.KHEIGHT))

    def test_convert_height_dir_none_matrix(self):
        dir_ = EHeightConvDir.NONE
        h = self.model.convert_height(self.LON, self.LAT, self.KHEIGHT, dir_)
        npt.assert_allclose(h, np.full_like(h, self.KHEIGHT))


if __name__ == '__main__':
    unittest.main()
