import os
import shutil
import pathlib
import datetime
import tempfile
import unittest

import numpy as np
from numpy import testing as npt

from geomodels import MagneticFieldModel, get_default_data_path
from geomodels.tests.utils import dms_to_dec


class StaticMethodsTestCase(unittest.TestCase):
    def test_default_magnetic_path(self):
        self.assertIsInstance(MagneticFieldModel.default_magnetic_path(), str)
        self.assertEqual(
            pathlib.Path(MagneticFieldModel.default_magnetic_path()),
            pathlib.Path(get_default_data_path()).joinpath("magnetic"),
        )

    def test_default_magnetic_name(self):
        names = (
            "wmm2010",
            "wmm2015",
            "wmm2015v2",
            "wmm2020",
            "wmm2025",
            "wmmhr2025",
            "igrf11",
            "igrf12",
            "igrf13",
            "igrf14",
            "emm2010",
            "emm2015",
            "emm2017",
        )
        self.assertTrue(MagneticFieldModel.default_magnetic_name() in names)


class InstantiationTestCase00(unittest.TestCase):
    def test_no_args(self):
        model = MagneticFieldModel()
        self.assertIsInstance(model, MagneticFieldModel)
        self.assertEqual(
            model.magnetic_model_name(),
            MagneticFieldModel.default_magnetic_name(),
        )


class InstantiationTestCase01(unittest.TestCase):
    MODEL_NAME = "wmm2015"

    def test_name(self):
        model = MagneticFieldModel(self.MODEL_NAME)
        self.assertIsInstance(model, MagneticFieldModel)
        self.assertEqual(model.magnetic_model_name(), self.MODEL_NAME)

    def test_default_path(self):
        path = MagneticFieldModel.default_magnetic_path()
        model = MagneticFieldModel(self.MODEL_NAME, path)
        self.assertEqual(model.magnetic_model_name(), self.MODEL_NAME)
        self.assertEqual(model.magnetic_model_directory(), path)

    def test_custom_path(self):
        default_path = MagneticFieldModel.default_magnetic_path()
        with tempfile.TemporaryDirectory() as dirname:
            magnetic_path = os.path.join(
                dirname, os.path.basename(default_path)
            )
            shutil.copytree(default_path, magnetic_path)
            model = MagneticFieldModel(self.MODEL_NAME, magnetic_path)
            self.assertEqual(model.magnetic_model_name(), self.MODEL_NAME)
            self.assertEqual(model.magnetic_model_directory(), magnetic_path)

    def test_custom_path_from_env01(self):
        default_path = pathlib.Path(MagneticFieldModel.default_magnetic_path())
        with tempfile.TemporaryDirectory() as dirname:
            magnetic_path = pathlib.Path(dirname) / default_path.name
            shutil.copytree(default_path, magnetic_path)

            old_env = os.environ.get("GEOGRAPHICLIB_DATA")
            os.environ["GEOGRAPHICLIB_DATA"] = dirname
            try:
                model = MagneticFieldModel(self.MODEL_NAME)
                self.assertEqual(model.magnetic_model_name(), self.MODEL_NAME)
                self.assertEqual(
                    pathlib.Path(model.magnetic_model_directory()),
                    magnetic_path,
                )
            finally:
                if old_env is None:
                    del os.environ["GEOGRAPHICLIB_DATA"]
                else:
                    os.environ["GEOGRAPHICLIB_DATA"] = old_env

    def test_custom_path_from_env02(self):
        default_path = MagneticFieldModel.default_magnetic_path()
        with tempfile.TemporaryDirectory() as dirname:
            magnetic_path = os.path.join(
                dirname, os.path.basename(default_path)
            )
            shutil.copytree(default_path, magnetic_path)

            old_env = os.environ.get("GEOGRAPHICLIB_MAGNETIC_PATH")
            os.environ["GEOGRAPHICLIB_MAGNETIC_PATH"] = magnetic_path
            try:
                model = MagneticFieldModel(self.MODEL_NAME)
                self.assertEqual(model.magnetic_model_name(), self.MODEL_NAME)
                self.assertEqual(
                    model.magnetic_model_directory(), magnetic_path
                )
            finally:
                if old_env is None:
                    del os.environ["GEOGRAPHICLIB_MAGNETIC_PATH"]
                else:
                    os.environ["GEOGRAPHICLIB_MAGNETIC_PATH"] = old_env


class InstantiationTestCase02(InstantiationTestCase01):
    MODEL_NAME = "igrf12"


class InfoMethodsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.name = MagneticFieldModel.default_magnetic_name()
        self.datapath = MagneticFieldModel.default_magnetic_path()
        self.model = MagneticFieldModel(self.name, self.datapath)

    def test_description(self):
        description = self.model.description()
        self.assertIsInstance(description, str)
        self.assertNotEqual(description, "NONE")

    def test_datetime(self):
        datestr = self.model.datetime()
        self.assertIsInstance(datestr, str)
        self.assertNotEqual(datestr, "UNKNOWN")
        date = datetime.datetime.strptime(datestr, "%Y-%m-%d")
        # date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        self.assertLess(date, datetime.datetime.now())

    def test_magnetic_file(self):
        filename = self.model.magnetic_file()
        self.assertIn(self.name, filename)
        self.assertIn(self.datapath, filename)

    def test_magnetic_model_name(self):
        name = self.model.magnetic_model_name()
        self.assertEqual(name, self.name)

    def test_magnetic_model_directory(self):
        path = self.model.magnetic_model_directory()
        self.assertEqual(path, self.datapath)

    def test_min_height(self):
        self.assertIsInstance(self.model.min_height(), float)

    def test_max_height(self):
        self.assertIsInstance(self.model.max_height(), float)
        self.assertGreater(self.model.max_height(), 0)

    def test_min_max_height(self):
        self.assertLess(self.model.min_height(), self.model.max_height())

    def test_min_time(self):
        self.assertIsInstance(self.model.min_time(), float)
        min_times = {
            "emm2010": 2010,
            "emm2015": 2000,
            "emm2017": 2000,
            "igrf11": 1900,
            "igrf12": 1900,
            "igrf13": 1900,
            "igrf14": 1900,
            "wmm2010": 2010,
            "wmm2015v2": 2015,
            "wmm2015": 2015,
            "wmm2020": 2020,
            "wmm2025": 2025,
            "wmmhr2025": 2025,
        }
        if self.name in min_times:
            self.assertEqual(self.model.min_time(), min_times[self.name])
        else:
            self.assertLess(self.model.min_time(), datetime.date.today().year)

    def test_max_time(self):
        self.assertIsInstance(self.model.max_time(), float)
        max_times = {
            "emm2010": 2015,
            "emm2015": 2020,
            "emm2017": 2022,
            "igrf11": 2015,
            "igrf12": 2020,
            "igrf13": 2025,
            "igrf14": 2030,
            "wmm2010": 2015,
            "wmm2015v2": 2020,
            "wmm2015": 2020,
            "wmm2020": 2025,
            "wmm2025": 2030,
            "wmmhr2025": 2030,
        }
        if self.name in max_times:
            self.assertEqual(self.model.max_time(), max_times[self.name])
        else:
            self.assertGreater(
                self.model.max_time(), datetime.date.today().year
            )

    def test_min_max_time(self):
        self.assertLess(self.model.min_time(), self.model.max_time())

    def test_major_radius(self):
        self.assertIsInstance(self.model.equatorial_radius(), float)
        self.assertGreater(self.model.equatorial_radius(), 5e6)

    def test_flattening(self):
        self.assertIsInstance(self.model.flattening(), float)
        self.assertGreater(self.model.flattening(), 0)
        self.assertLess(self.model.flattening(), 1)

    def test_degree(self):
        self.assertIsInstance(self.model.degree(), int)
        self.assertGreaterEqual(self.model.degree(), 0)
        self.assertLessEqual(self.model.degree(), 360)

    def test_order(self):
        self.assertIsInstance(self.model.order(), int)
        self.assertGreater(self.model.order(), 0)
        self.assertLessEqual(self.model.order(), 12)


class ComputationTestCase(unittest.TestCase):
    # MODEL_NAME = MagneticFieldModel.default_magnetic_name()
    MODEL_NAME = "wmm2015"

    YEAR = 2016.0  # 2016-01-01
    LAT = +dms_to_dec(16, 46, 33)  # 16:46:33N
    LON = -dms_to_dec(3, 0, 34)  # 03:00:34W
    HEIGHT = +300  # [m]

    BX = -1251.3634113  # NOTE: east component (5th item)
    BY = +33848.7341446  # NOTE: north component (4th item)
    BZ = -7293.8535382  # NOTE: inverted sign
    BXT = +53.6988656  # NOTE: east component (5th item, second line)
    BYT = +33.7765829  # NOTE: north component (4th item, second line)
    BZT = +41.3769946  # NOTE: inverted sign
    H = +33871.8572503
    F = +34648.2757582
    D = -2.11721965
    I = +12.15231735  # noqa: E741

    # $ echo 2016-01-01 16:46:33N 3:00:34W 300 | MagneticField -r -p 7
    # -2.11721965 12.15231735 33871.8572503 33848.7341446 \
    # -1251.3634113 7293.8535382 34648.2757582
    # 0.09288284 -0.07794874 31.7696715 33.7765829 \
    # 53.6988656 -41.3769946 22.3474336
    #
    # $ echo 2016.0 16.775833333333335 -3.0094444444444446 300 | \
    # MagneticField -r -p 7
    # -2.11721965 12.15231735 33871.8572503 33848.7341446 \
    # -1251.3634113 7293.8535382 34648.2757582
    # 0.09288284 -0.07794874 31.7696715 33.7765829 \
    # 53.6988656 -41.3769946 22.3474336

    def setUp(self) -> None:
        self.model = MagneticFieldModel(self.MODEL_NAME)

    def test_field_components(self):
        H, F, D, I = MagneticFieldModel.field_components(  # noqa: E741,N806
            self.BX, self.BY, self.BZ
        )
        npt.assert_allclose([H, F, D, I], [self.H, self.F, self.D, self.I])

    # @TODO
    # def test_field_components_and_rate(self):
    #     pass

    # @TODO
    # def test_circle(self):
    #     pass

    def test_compute_scalar(self):
        fld_x, fld_y, fld_z = self.model(
            self.YEAR, self.LAT, self.LON, self.HEIGHT
        )
        npt.assert_allclose([fld_x, fld_y, fld_z], [self.BX, self.BY, self.BZ])

    def test_compute_scalar_with_rate(self):
        (fld_x, fld_y, fld_z, fld_xt, fld_yt, fld_zt) = (
            self.model.compute_with_rate(
                self.YEAR, self.LAT, self.LON, self.HEIGHT
            )
        )
        npt.assert_allclose([fld_x, fld_y, fld_z], [self.BX, self.BY, self.BZ])
        npt.assert_allclose(
            [fld_xt, fld_yt, fld_zt], [self.BXT, self.BYT, self.BZT]
        )


class VectorComputationTestCase(unittest.TestCase):
    # MODEL_NAME = MagneticFieldModel.default_magnetic_name()
    MODEL_NAME = "wmm2015"

    YEAR = 2016.0
    LAT = np.asarray(
        [
            [+dms_to_dec(16, 46, 33), -dms_to_dec(16, 46, 43)],
            [-dms_to_dec(16, 56, 33), +dms_to_dec(16, 56, 43)],
        ]
    )
    LON = np.asarray(
        [
            [-dms_to_dec(3, 0, 34), +dms_to_dec(3, 0, 44)],
            [+dms_to_dec(3, 10, 34), -dms_to_dec(3, 10, 44)],
        ]
    )
    HEIGHT = np.asarray(
        [
            [+300, +400000],
            [+400000, +300],
        ]
    )
    BX = np.asarray(
        [
            [-1251.3634113, -2917.6087863],
            [-2908.0688421, -1262.5153146],
        ]
    )
    BY = np.asarray(
        [
            [+33848.7341446, +13455.1508250],
            [+13378.9665352, +33836.6298435],
        ]
    )
    BZ = np.asarray(
        [
            [-7293.85353820, +20132.4047379],
            [+20169.4124889, -7539.67870600],
        ]
    )
    BXT = np.asarray(
        [
            [+53.6988656, +48.1739432],
            [+48.0353017, +53.7715374],
        ]
    )
    BYT = np.asarray(
        [
            [+33.7765829, -37.4184172],
            [-37.5102493, +33.9119117],
        ]
    )
    BZT = np.asarray(
        [
            [+41.3769946, +28.8842256],
            [+27.8740361, +41.1851008],
        ]
    )
    H = np.asarray(
        [
            [+33871.8572503, +13767.8438673],
            [+13691.3699073, +33860.1751928],
        ]
    )
    F = np.asarray(
        [
            [+34648.2757582, +24389.9004772],
            [+24377.4241889, +34689.4540037],
        ]
    )
    D = np.asarray(
        [
            [-2.117219650, -12.23458341],
            [-12.26312924, -2.136833910],
        ]
    )
    I = np.asarray(  # noqa: E741
        [
            [+12.15231735, -55.63314796],
            [-55.83061445, +12.55330784],
        ]
    )

    def setUp(self) -> None:
        self.model = MagneticFieldModel(self.MODEL_NAME)

    def test_field_components_vector(self):
        H, F, D, I = MagneticFieldModel.field_components(  # noqa: E741,N806
            self.BX.flatten(), self.BY.flatten(), self.BZ.flatten()
        )
        npt.assert_allclose(H, self.H.flatten())
        npt.assert_allclose(F, self.F.flatten())
        npt.assert_allclose(D, self.D.flatten())
        npt.assert_allclose(I, self.I.flatten())

    def test_field_components_matrix(self):
        H, F, D, I = MagneticFieldModel.field_components(  # noqa: E741,N806
            self.BX, self.BY, self.BZ
        )
        npt.assert_allclose(H, self.H)
        npt.assert_allclose(F, self.F)
        npt.assert_allclose(D, self.D)
        npt.assert_allclose(I, self.I)

    # @TODO
    # def test_field_components_and_rate_xxx(self):
    #     pass

    # @TODO
    # def test_circle_xxx(self):
    #     pass

    def test_compute_vector(self):
        fld_x, fld_y, fld_z = self.model(
            self.YEAR,
            self.LAT.flatten(),
            self.LON.flatten(),
            self.HEIGHT.flatten(),
        )
        npt.assert_allclose(fld_x, self.BX.flatten())
        npt.assert_allclose(fld_y, self.BY.flatten())
        npt.assert_allclose(fld_z, self.BZ.flatten())

    def test_compute_vector_with_rate(self):
        (fld_x, fld_y, fld_z, fld_xt, fld_yt, fld_zt) = (
            self.model.compute_with_rate(
                self.YEAR,
                self.LAT.flatten(),
                self.LON.flatten(),
                self.HEIGHT.flatten(),
            )
        )
        npt.assert_allclose(fld_x, self.BX.flatten())
        npt.assert_allclose(fld_y, self.BY.flatten())
        npt.assert_allclose(fld_z, self.BZ.flatten())
        npt.assert_allclose(fld_xt, self.BXT.flatten())
        npt.assert_allclose(fld_yt, self.BYT.flatten())
        npt.assert_allclose(fld_zt, self.BZT.flatten())

    def test_compute_matrix(self):
        fld_x, fld_y, fld_z = self.model(
            self.YEAR, self.LAT, self.LON, self.HEIGHT
        )
        npt.assert_allclose(fld_x, self.BX)
        npt.assert_allclose(fld_y, self.BY)
        npt.assert_allclose(fld_z, self.BZ)

    def test_compute_matrix_with_rate(self):
        (fld_x, fld_y, fld_z, fld_xt, fld_yt, fld_zt) = (
            self.model.compute_with_rate(
                self.YEAR, self.LAT, self.LON, self.HEIGHT
            )
        )
        npt.assert_allclose(fld_x, self.BX)
        npt.assert_allclose(fld_y, self.BY)
        npt.assert_allclose(fld_z, self.BZ)
        npt.assert_allclose(fld_xt, self.BXT)
        npt.assert_allclose(fld_yt, self.BYT)
        npt.assert_allclose(fld_zt, self.BZT)


class ConstHeightVectorComputationTestCase(unittest.TestCase):
    # MODEL_NAME = MagneticFieldModel.default_magnetic_name()
    MODEL_NAME = "wmm2015"

    YEAR = 2016.0
    LAT = np.asarray(
        [
            [+dms_to_dec(16, 46, 33), +dms_to_dec(16, 56, 43)],
            [+dms_to_dec(16, 46, 33), +dms_to_dec(16, 56, 43)],
        ]
    )
    LON = np.asarray(
        [
            [-dms_to_dec(3, 0, 34), -dms_to_dec(3, 10, 44)],
            [-dms_to_dec(3, 0, 34), -dms_to_dec(3, 10, 44)],
        ]
    )
    HEIGHT = +300
    BX = np.asarray(
        [
            [-1251.3634113, -1262.5153146],
            [-1251.3634113, -1262.5153146],
        ]
    )
    BY = np.asarray(
        [
            [+33848.7341446, +33836.6298435],
            [+33848.7341446, +33836.6298435],
        ]
    )
    BZ = np.asarray(
        [
            [-7293.85353820, -7539.67870600],
            [-7293.85353820, -7539.67870600],
        ]
    )
    BXT = np.asarray(
        [
            [+53.6988656, +53.7715374],
            [+53.6988656, +53.7715374],
        ]
    )
    BYT = np.asarray(
        [
            [+33.7765829, +33.9119117],
            [+33.7765829, +33.9119117],
        ]
    )
    BZT = np.asarray(
        [
            [+41.3769946, +41.1851008],
            [+41.3769946, +41.1851008],
        ]
    )
    H = np.asarray(
        [
            [+33871.8572503, +33860.1751928],
            [+33871.8572503, +33860.1751928],
        ]
    )
    F = np.asarray(
        [
            [+34648.2757582, +34689.4540037],
            [+34648.2757582, +34689.4540037],
        ]
    )
    D = np.asarray(
        [
            [-2.11721965, -2.13683391],
            [-2.11721965, -2.13683391],
        ]
    )
    I = np.asarray(  # noqa: E741
        [
            [+12.15231735, +12.55330784],
            [+12.15231735, +12.55330784],
        ]
    )

    def setUp(self) -> None:
        self.model = MagneticFieldModel(self.MODEL_NAME)

    # @TODO
    # def test_circle_xxx(self):
    #     pass

    def test_compute_vector(self):
        fld_x, fld_y, fld_z = self.model(
            self.YEAR, self.LAT.flatten(), self.LON.flatten(), self.HEIGHT
        )
        npt.assert_allclose(fld_x, self.BX.flatten())
        npt.assert_allclose(fld_y, self.BY.flatten())
        npt.assert_allclose(fld_z, self.BZ.flatten())

    def test_compute_vector_with_rate(self):
        (fld_x, fld_y, fld_z, fld_xt, fld_yt, fld_zt) = (
            self.model.compute_with_rate(
                self.YEAR,
                self.LAT.flatten(),
                self.LON.flatten(),
                self.HEIGHT,
            )
        )
        npt.assert_allclose(fld_x, self.BX.flatten())
        npt.assert_allclose(fld_y, self.BY.flatten())
        npt.assert_allclose(fld_z, self.BZ.flatten())
        npt.assert_allclose(fld_xt, self.BXT.flatten())
        npt.assert_allclose(fld_yt, self.BYT.flatten())
        npt.assert_allclose(fld_zt, self.BZT.flatten())

    def test_compute_matrix(self):
        fld_x, fld_y, fld_z = self.model(
            self.YEAR, self.LAT, self.LON, self.HEIGHT
        )
        npt.assert_allclose(fld_x, self.BX)
        npt.assert_allclose(fld_y, self.BY)
        npt.assert_allclose(fld_z, self.BZ)

    def test_compute_matrix_with_rate(self):
        (fld_x, fld_y, fld_z, fld_xt, fld_yt, fld_zt) = (
            self.model.compute_with_rate(
                self.YEAR, self.LAT, self.LON, self.HEIGHT
            )
        )
        npt.assert_allclose(fld_x, self.BX)
        npt.assert_allclose(fld_y, self.BY)
        npt.assert_allclose(fld_z, self.BZ)
        npt.assert_allclose(fld_xt, self.BXT)
        npt.assert_allclose(fld_yt, self.BYT)
        npt.assert_allclose(fld_zt, self.BZT)
