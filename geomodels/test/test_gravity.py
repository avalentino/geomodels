# -*- coding: utf-8 -*-

import os
import shutil
import pathlib
import datetime
import tempfile
import unittest

import numpy as np
from numpy import testing as npt

from geomodels import GravityModel
from geomodels import get_default_data_path
from geomodels.test.utils import dms_to_dec


class StaticMethodsTestCase(unittest.TestCase):
    def test_default_gravity_path(self):
        self.assertIsInstance(
            GravityModel.default_gravity_path(), str)
        self.assertEqual(
            GravityModel.default_gravity_path(),
            os.path.join(get_default_data_path(), 'gravity')
        )

    def test_default_gravity_name(self):
        names = (
            'egm84',
            'egm96',
            'egm2008',
            'wgs84',
        )
        self.assertTrue(GravityModel.default_gravity_name() in names)


class InstantiationTestCase(unittest.TestCase):
    MODEL_NAME = 'egm96'

    def test_name(self):
        model = GravityModel(self.MODEL_NAME)
        self.assertIsInstance(model, GravityModel)
        self.assertEqual(model.gravity_model_name(), self.MODEL_NAME)

    def test_default_path(self):
        path = GravityModel.default_gravity_path()
        model = GravityModel(self.MODEL_NAME, path)
        self.assertEqual(model.gravity_model_name(), self.MODEL_NAME)
        self.assertEqual(model.gravity_model_directory(), path)

    def test_custom_path(self):
        default_path = pathlib.Path(GravityModel.default_gravity_path())
        with tempfile.TemporaryDirectory() as dirname:
            gravity_model_path = pathlib.Path(dirname) / default_path.name
            gravity_model_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, gravity_model_path)

            model = GravityModel(self.MODEL_NAME, gravity_model_path)
            self.assertEqual(model.gravity_model_name(), self.MODEL_NAME)
            self.assertEqual(
                model.gravity_model_directory(), str(gravity_model_path))

    def test_custom_path_from_env01(self):
        default_path = pathlib.Path(GravityModel.default_gravity_path())
        with tempfile.TemporaryDirectory() as dirname:
            gravity_model_path = pathlib.Path(dirname) / default_path.name
            gravity_model_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, gravity_model_path)

            old_env = os.environ.get('GEOGRAPHICLIB_DATA')
            os.environ['GEOGRAPHICLIB_DATA'] = dirname
            try:
                model = GravityModel(self.MODEL_NAME)
                self.assertEqual(model.gravity_model_name(), self.MODEL_NAME)
                self.assertEqual(
                    model.gravity_model_directory(), str(gravity_model_path))
            finally:
                if old_env is None:
                    del os.environ['GEOGRAPHICLIB_DATA']
                else:
                    os.environ['GEOGRAPHICLIB_DATA'] = old_env

    def test_custom_path_from_env02(self):
        default_path = pathlib.Path(GravityModel.default_gravity_path())
        with tempfile.TemporaryDirectory() as dirname:
            gravity_model_path = pathlib.Path(dirname) / default_path.name
            gravity_model_path.mkdir()
            for filename in default_path.glob(f'{self.MODEL_NAME}*'):
                shutil.copy(filename, gravity_model_path)

            old_env = os.environ.get('GEOGRAPHICLIB_GRAVITY_PATH')
            os.environ['GEOGRAPHICLIB_GRAVITY_PATH'] = str(gravity_model_path)
            try:
                model = GravityModel(self.MODEL_NAME)
                self.assertEqual(model.gravity_model_name(), self.MODEL_NAME)
                self.assertEqual(
                    model.gravity_model_directory(), str(gravity_model_path))
            finally:
                if old_env is None:
                    del os.environ['GEOGRAPHICLIB_GRAVITY_PATH']
                else:
                    os.environ['GEOGRAPHICLIB_GRAVITY_PATH'] = old_env


class InfoMethodsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.name = GravityModel.default_gravity_name()
        self.datapath = GravityModel.default_gravity_path()
        self.model = GravityModel(self.name, self.datapath)

    def test_description(self):
        description = self.model.description()
        self.assertIsInstance(description, str)
        self.assertNotEqual(description, 'NONE')

    def test_datetime(self):
        datestr = self.model.datetime()
        self.assertIsInstance(datestr, str)
        self.assertNotEqual(datestr, 'UNKNOWN')
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        # date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        self.assertLess(date, datetime.datetime.now())

    def test_gravity_file(self):
        filename = self.model.gravity_file()
        self.assertIn(self.name, filename)
        self.assertIn(self.datapath, filename)

    def test_gravity_model_name(self):
        name = self.model.gravity_model_name()
        self.assertEqual(name, self.name)

    def test_gravity_model_directory(self):
        path = self.model.gravity_model_directory()
        self.assertEqual(path, self.datapath)

    def equator_radius(self):
        self.assertIsInstance(self.model.equator_radius(), float)
        self.assertGreater(self.model.equator_radius(), 5e6)

    def test_flattening(self):
        self.assertIsInstance(self.model.flattening(), float)
        self.assertGreater(self.model.flattening(), 0)
        self.assertLess(self.model.flattening(), 1)

    def test_mass_constant(self):
        self.assertIsInstance(self.model.mass_constant(), float)
        self.assertGreater(self.model.mass_constant(), 0)

    def test_reference_mass_constant(self):
        self.assertIsInstance(self.model.reference_mass_constant(), float)
        self.assertGreater(self.model.reference_mass_constant(), 0)

    def test_angular_velocity(self):
        self.assertIsInstance(self.model.angular_velocity(), float)
        self.assertGreater(self.model.angular_velocity(), 0)


class ComputationTestCase(unittest.TestCase):
    MODEL_NAME = 'egm96'

    LAT = +dms_to_dec(27, 59, 17)   # 27:59:17N
    LON = +dms_to_dec(86, 55, 32)   # 86:55:32E
    HEIGHT = +8820.0                # [m]

    X = 302714.     # [m]
    Y = 5636006.    # [m]
    Z = 2979476.    # [m]

    GX = -0.0002103214548  # [m/s**2]
    GY = +0.0008380880427  # [m/s**2]
    GZ = -9.7665319359240  # [m/s**2]

    MGAL = 1.e-5                        # [m/s**2]
    DELTAX = -21.03214547840420 * MGAL  # [m/s**2]
    DELTAY = +89.75849905064960 * MGAL  # [m/s**2]
    DELTAZ = -199.4330543962868 * MGAL  # [m/s**2]

    GHEIGHT = -28.743736628353

    ARCSEC = 1./3600.
    DG01 = +208.0275697808106 * MGAL  # [m/s**2]
    XI = -18.8435137999035 * ARCSEC   # [rad]
    ETA = +4.4428027084385 * ARCSEC   # [rad]

    # $ echo 27:59:17N 86:55:32E 8820 | Gravity -n egm96 -p 13
    # -0.0002103214548 0.0008380880427 -9.7665319359240
    # $ echo 27.988055555555555 86.92555555555556 8820 | Gravity -n egm96 -p 13 -G
    # -0.0002103214548 0.0008380880427 -9.7665319359240
    # $ echo 27.988055555555555 86.92555555555556 8820 | Gravity -n egm96 -p 13 -D
    # -21.0321454784042 89.7584990506496 -199.4330543962868
    # echo 27.988055555555555 86.92555555555556 | Gravity -n egm96 -p 13 -H
    # -28.743736628353
    # $ echo 27.988055555555555 86.92555555555556 8820 | Gravity -n egm96 -p 13 -A
    # 208.0275697808106 -18.8435137999035 4.4428027084385

    def setUp(self) -> None:
        self.model = GravityModel(self.MODEL_NAME)

    def test_gravity_scalar(self):
        w, gx, gy, gz = self.model.gravity(self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(gx, self.GX)
        npt.assert_allclose(gy, self.GY)
        npt.assert_allclose(gz, self.GZ)

    def test_disturbance_scalar(self):
        t, deltax, deltay, deltaz = self.model.disturbance(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(deltax, self.DELTAX)
        npt.assert_allclose(deltay, self.DELTAY)
        npt.assert_allclose(deltaz, self.DELTAZ)

    def test_geoid_heigt_scalar(self):
        gheight = self.model.geoid_height(self.LAT, self.LON)
        npt.assert_allclose(gheight, self.GHEIGHT)

    def test_spherical_anomaly_scalar(self):
        dg01, xi, eta = self.model.spherical_anomaly(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(dg01, self.DG01)
        npt.assert_allclose(xi, self.XI)
        npt.assert_allclose(eta, self.ETA)

    def test_w_scalar(self):
        w, gx, gy, gz = self.model.w(self.X, self.Y, self.Z)
        self.assertTrue(np.isscalar(w))
        self.assertTrue(np.isscalar(gx))
        self.assertTrue(np.isscalar(gy))
        self.assertTrue(np.isscalar(gz))

    def test_v_scalar(self):
        v, gx, gy, gz = self.model.v(self.X, self.Y, self.Z)
        self.assertTrue(np.isscalar(v))
        self.assertTrue(np.isscalar(gx))
        self.assertTrue(np.isscalar(gy))
        self.assertTrue(np.isscalar(gz))

    def test_t_components_scalar(self):
        t, gx, gy, gz = self.model.t_components(self.X, self.Y, self.Z)
        self.assertTrue(np.isscalar(t))
        self.assertTrue(np.isscalar(gx))
        self.assertTrue(np.isscalar(gy))
        self.assertTrue(np.isscalar(gz))

    def test_t_scalar(self):
        t = self.model.t(self.X, self.Y, self.Z)
        self.assertTrue(np.isscalar(t))

    def test_u_scalar(self):
        u, gammax, gammay, gammaz = self.model.u(self.X, self.Y, self.Z)
        self.assertTrue(np.isscalar(u))
        self.assertTrue(np.isscalar(gammax))
        self.assertTrue(np.isscalar(gammay))
        self.assertTrue(np.isscalar(gammaz))

    def test_phi_scalar(self):
        phi, fx, fy = self.model.phi(self.X, self.Y)
        self.assertTrue(np.isscalar(phi))
        self.assertTrue(np.isscalar(fx))
        self.assertTrue(np.isscalar(fy))


class VectorComputationTestCase(unittest.TestCase):
    MODEL_NAME = 'egm96'

    LAT = np.asarray([
        [+dms_to_dec(16, 46, 33), -dms_to_dec(16, 46, 43)],
        [-dms_to_dec(16, 56, 33), +dms_to_dec(16, 56, 43)],
    ])
    LON = np.asarray([
        [-dms_to_dec(3, 0, 34), +dms_to_dec(3, 0, 44)],
        [+dms_to_dec(3, 10, 34), -dms_to_dec(3, 10, 44)],
    ])
    HEIGHT = np.asarray([
        [+300, +400000],
        [+400000, +300],
    ])

    X = np.asarray([
        [6100258., 6482309.],
        [6475723., 6093852.],
    ])
    Y = np.asarray([
        [-320709., +341110.],
        [+359341., -338447.],
    ])
    Z = np.asarray([
        [+1829182., -1944859.],
        [-1963312., +1847129.],
    ])

    GX = np.asarray([
        [-0.0000185562383, +0.0000171252863],
        [+0.0000179414111, +0.0000255265776],
    ])
    GY = np.asarray([
        [-0.0000022160340, +0.0016776569530],
        [+0.0016913972644, -0.0000471425191],
    ])
    GZ = np.asarray([
        [-9.7839489045745, -8.6568801936947],
        [-8.6569658422907, -9.7840427535630],
    ])

    MGAL = 1.e-5  # [m/s**2]
    DELTAX = np.asarray([
        [-1.8556238327792, +1.7125286304307],
        [+1.7941411100352, +2.5526577571442],
    ]) * MGAL
    DELTAY = np.asarray([
        [-0.0864975107851, -4.2925736778895],
        [-4.3994466419252, -4.5779437005530],
    ]) * MGAL
    DELTAZ = np.asarray([
        [-24.6995051809167, -3.77044400298770],
        [-3.89353944957160, -25.6012585484130],
    ]) * MGAL

    GHEIGHT = np.asarray([
        [+28.707423353273, +14.886288004977],
        [+15.032497786636, +28.660865719440],
    ])

    ARCSEC = 1./3600.
    DG01 = np.asarray([
        [+15.7255802520963, -0.28121454847100],
        [-0.19222301397180, +16.6326172077381],
    ]) * MGAL
    XI = np.asarray([
        [+0.0278739163708, +1.0212161827314],
        [+1.0466052916775, +0.9752134528843],
    ]) * ARCSEC
    ETA = np.asarray([
        [+0.3912117252501, -0.4080406679571],
        [-0.4274821365431, -0.5381591725495],
    ]) * ARCSEC

    def setUp(self) -> None:
        self.model = GravityModel(self.MODEL_NAME)

    def test_gravity_vector(self):
        w, gx, gy, gz = self.model.gravity(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT.flatten())
        npt.assert_allclose(gx, self.GX.flatten())
        npt.assert_allclose(gy, self.GY.flatten())
        npt.assert_allclose(gz, self.GZ.flatten())

    def test_gravity_matrix(self):
        w, gx, gy, gz = self.model.gravity(self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(gx, self.GX)
        npt.assert_allclose(gy, self.GY)
        npt.assert_allclose(gz, self.GZ)

    def test_disturbance_vector(self):
        t, deltax, deltay, deltaz = self.model.disturbance(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT.flatten())
        npt.assert_allclose(deltax, self.DELTAX.flatten())
        npt.assert_allclose(deltay, self.DELTAY.flatten())
        npt.assert_allclose(deltaz, self.DELTAZ.flatten())

    def test_disturbance_matrix(self):
        t, deltax, deltay, deltaz = self.model.disturbance(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(deltax, self.DELTAX)
        npt.assert_allclose(deltay, self.DELTAY)
        npt.assert_allclose(deltaz, self.DELTAZ)

    def test_geoid_heigt_vector(self):
        gheight = self.model.geoid_height(
            self.LAT.flatten(), self.LON.flatten())
        npt.assert_allclose(gheight, self.GHEIGHT.flatten())

    def test_geoid_heigt_matrix(self):
        gheight = self.model.geoid_height(self.LAT, self.LON)
        npt.assert_allclose(gheight, self.GHEIGHT)

    def test_spherical_anomaly_vector(self):
        dg01, xi, eta = self.model.spherical_anomaly(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT.flatten())
        npt.assert_allclose(dg01, self.DG01.flatten())
        npt.assert_allclose(xi, self.XI.flatten())
        npt.assert_allclose(eta, self.ETA.flatten())

    def test_spherical_anomaly_matrix(self):
        dg01, xi, eta = self.model.spherical_anomaly(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(dg01, self.DG01)
        npt.assert_allclose(xi, self.XI)
        npt.assert_allclose(eta, self.ETA)

    def test_w_vector(self):
        w, gx, gy, gz = self.model.w(
            self.X.flatten(), self.Y.flatten(), self.Z.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(w.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_w_matrix(self):
        w, gx, gy, gz = self.model.w(self.X, self.Y, self.Z)
        shape = self.X.shape
        self.assertEqual(w.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_v_vector(self):
        v, gx, gy, gz = self.model.v(
            self.X.flatten(), self.Y.flatten(), self.Z.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(v.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_v_matrix(self):
        v, gx, gy, gz = self.model.v(self.X, self.Y, self.Z)
        shape = self.X.shape
        self.assertEqual(v.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_t_components_vector(self):
        t, gx, gy, gz = self.model.t_components(
            self.X.flatten(), self.Y.flatten(), self.Z.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(t.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_t_components_matrix(self):
        t, gx, gy, gz = self.model.t_components(self.X, self.Y, self.Z)
        shape = self.X.shape
        self.assertEqual(t.shape, shape)
        self.assertEqual(gx.shape, shape)
        self.assertEqual(gy.shape, shape)
        self.assertEqual(gz.shape, shape)

    def test_t_vector(self):
        t = self.model.t(self.X.flatten(), self.Y.flatten(), self.Z.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(t.shape, shape)

    def test_t_matrix(self):
        t = self.model.t(self.X, self.Y, self.Z)
        shape = self.X.shape
        self.assertEqual(t.shape, shape)

    def test_u_vector(self):
        u, gammax, gammay, gammaz = self.model.u(
            self.X.flatten(), self.Y.flatten(), self.Z.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(u.shape, shape)
        self.assertEqual(gammax.shape, shape)
        self.assertEqual(gammay.shape, shape)
        self.assertEqual(gammaz.shape, shape)

    def test_u_matrix(self):
        u, gammax, gammay, gammaz = self.model.u(self.X, self.Y, self.Z)
        shape = self.X.shape
        self.assertEqual(u.shape, shape)
        self.assertEqual(gammax.shape, shape)
        self.assertEqual(gammay.shape, shape)
        self.assertEqual(gammaz.shape, shape)

    def test_phi_vector(self):
        phi, fx, fy = self.model.phi(self.X.flatten(), self.Y.flatten())
        shape = self.X.flatten().shape
        self.assertEqual(phi.shape, shape)
        self.assertEqual(fx.shape, shape)
        self.assertEqual(fy.shape, shape)

    def test_phi_matrix(self):
        phi, fx, fy = self.model.phi(self.X, self.Y)
        shape = self.X.shape
        self.assertEqual(phi.shape, shape)
        self.assertEqual(fx.shape, shape)
        self.assertEqual(fy.shape, shape)


class ConstHeightVectorComputationTestCase(unittest.TestCase):
    MODEL_NAME = 'egm96'

    LAT = np.asarray([
        [+dms_to_dec(16, 46, 33), -dms_to_dec(16, 46, 43)],
        [-dms_to_dec(16, 56, 33), +dms_to_dec(16, 56, 43)],
    ])
    LON = np.asarray([
        [-dms_to_dec(3, 0, 34), +dms_to_dec(3, 0, 44)],
        [+dms_to_dec(3, 10, 34), -dms_to_dec(3, 10, 44)],
    ])
    HEIGHT = 300.

    GX = np.asarray([
        [-0.0000185562383, +0.0000064699387],
        [+0.0000003420218, +0.0000255265776],
    ])
    GY = np.asarray([
        [-0.0000022160340, -0.0000728579276],
        [-0.0000753687802, -0.0000471425191],
    ])
    GZ = np.asarray([
        [-9.7839489045745, -9.7837475302880],
        [-9.7838283874308, -9.7840427535630],
    ])

    MGAL = 1.e-5  # [m/s**2]
    DELTAX = np.asarray([
        [-1.8556238327792, +0.6469938707953],
        [+0.0342021784554, +2.5526577571442],
    ]) * MGAL
    DELTAY = np.asarray([
        [-0.0864975107851, -7.4209183975897],
        [-7.6731665518214, -4.5779437005530],
    ]) * MGAL
    DELTAZ = np.asarray([
        [-24.6995051809167, -4.42361602478520],
        [-4.30431998082860, -25.6012585484130],
    ]) * MGAL

    GHEIGHT = np.asarray([
        [+28.707423353273, +14.886288004977],
        [+15.032497786636, +28.660865719440],
    ])

    ARCSEC = 1./3600.
    DG01 = np.asarray([
        [+15.7255802520963, -0.2935186685049],
        [-0.4570089444766, +16.6326172077381],
    ]) * MGAL
    XI = np.asarray([
        [+0.0278739163708, +1.5627851282352],
        [+1.6159837030728, +0.9752134528843],
    ]) * ARCSEC
    ETA = np.asarray([
        [+0.3912117252501, -0.1364024044788],
        [-0.0072106096609, -0.5381591725495],
    ]) * ARCSEC

    def setUp(self) -> None:
        self.model = GravityModel(self.MODEL_NAME)

    def test_gravity_vector(self):
        w, gx, gy, gz = self.model.gravity(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT)
        npt.assert_allclose(gx, self.GX.flatten())
        npt.assert_allclose(gy, self.GY.flatten())
        npt.assert_allclose(gz, self.GZ.flatten())

    def test_gravity_matrix(self):
        w, gx, gy, gz = self.model.gravity(self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(gx, self.GX)
        npt.assert_allclose(gy, self.GY)
        npt.assert_allclose(gz, self.GZ)

    def test_disturbance_vector(self):
        t, deltax, deltay, deltaz = self.model.disturbance(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT)
        npt.assert_allclose(deltax, self.DELTAX.flatten())
        npt.assert_allclose(deltay, self.DELTAY.flatten())
        npt.assert_allclose(deltaz, self.DELTAZ.flatten())

    def test_disturbance_matrix(self):
        t, deltax, deltay, deltaz = self.model.disturbance(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(deltax, self.DELTAX)
        npt.assert_allclose(deltay, self.DELTAY)
        npt.assert_allclose(deltaz, self.DELTAZ)

    def test_spherical_anomaly_vector(self):
        dg01, xi, eta = self.model.spherical_anomaly(
            self.LAT.flatten(), self.LON.flatten(), self.HEIGHT)
        npt.assert_allclose(dg01, self.DG01.flatten())
        npt.assert_allclose(xi, self.XI.flatten())
        npt.assert_allclose(eta, self.ETA.flatten())

    def test_spherical_anomaly_matrix(self):
        dg01, xi, eta = self.model.spherical_anomaly(
            self.LAT, self.LON, self.HEIGHT)
        npt.assert_allclose(dg01, self.DG01)
        npt.assert_allclose(xi, self.XI)
        npt.assert_allclose(eta, self.ETA)


if __name__ == '__main__':
    unittest.main()
