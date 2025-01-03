import os
import shutil
import pathlib
import tempfile
import unittest
from unittest import mock
from urllib.parse import urlsplit

import geomodels.data


class DataPathTestCase(unittest.TestCase):
    def test_default_data_path(self):
        path = geomodels.data.get_default_data_path()
        self.assertTrue(os.path.exists(path))

    def test_default_data_path_from_env(self):
        old_env = os.environ.get("GEOGRAPHICLIB_DATA")
        dummy_path = "/dummy/path"
        os.environ["GEOGRAPHICLIB_DATA"] = dummy_path

        try:
            path = geomodels.data.get_default_data_path()
            self.assertEqual(path, dummy_path)
        finally:
            if old_env is None:
                del os.environ["GEOGRAPHICLIB_DATA"]
            else:
                os.environ["GEOGRAPHICLIB_DATA"] = old_env


class UrlTestCase(unittest.TestCase):
    MODEL_TYPES = [
        geomodels.data.EGeoidModel,
        geomodels.data.EGravityModel,
        geomodels.data.EMagneticModel,
    ]

    def test_get_base_url(self):
        self.assertIsInstance(geomodels.data.get_base_url(), str)

    def test_get_model_url(self):
        base_url = geomodels.data.get_base_url()
        archive_extension = geomodels.data.EArchiveType.BZ2.value
        model: geomodels.data.GenericModelType
        for model_type in self.MODEL_TYPES:
            for model in model_type:  # type: ignore[assignment]
                with self.subTest(model=model):
                    url = geomodels.data.get_model_url(model)
                    self.assertIsInstance(url, str)
                    self.assertTrue(url.startswith(base_url))
                    urlobj = urlsplit(url)
                    self.assertIn(model.get_model_type().value, urlobj.path)
                    self.assertIn(model.value, urlobj.path)
                    self.assertTrue(urlobj.path.endswith(archive_extension))

    def test_get_model_url_with_base_url(self):
        base_url = "https://dummy.url"
        archive_extension = geomodels.data.EArchiveType.BZ2.value
        model: geomodels.data.GenericModelType
        for model_type in self.MODEL_TYPES:
            for model in model_type:  # type: ignore[assignment]
                with self.subTest(model=model):
                    url = geomodels.data.get_model_url(
                        model, base_url=base_url
                    )
                    self.assertIsInstance(url, str)
                    self.assertTrue(url.startswith(base_url))
                    urlobj = urlsplit(url)
                    self.assertIn(model.get_model_type().value, urlobj.path)
                    self.assertIn(model.value, urlobj.path)
                    self.assertTrue(urlobj.path.endswith(archive_extension))

    def test_get_model_url_with_archive_type(self):
        base_url = geomodels.data.get_base_url()
        archive_type = geomodels.data.EArchiveType.ZIP
        archive_extension = archive_type.value
        model: geomodels.data.GenericModelType
        for model_type in self.MODEL_TYPES:
            for model in model_type:  # type: ignore[assignment]
                with self.subTest(model=model):
                    url = geomodels.data.get_model_url(
                        model, archive_type=archive_type
                    )
                    self.assertIsInstance(url, str)
                    self.assertTrue(url.startswith(base_url))
                    urlobj = urlsplit(url)
                    self.assertIn(model.get_model_type().value, urlobj.path)
                    self.assertIn(model.value, urlobj.path)
                    self.assertTrue(urlobj.path.endswith(archive_extension))


class DownloadTestCase(unittest.TestCase):
    DATA = "dummydata"

    def setUp(self) -> None:
        self.datadir = pathlib.Path(tempfile.mkdtemp())
        self.srcfile = self.datadir / "filename.txt"
        with open(self.srcfile, "w") as fd:
            fd.write(self.DATA)

    def tearDown(self) -> None:
        shutil.rmtree(self.datadir)

    def test_download_file_uri(self):
        dstdir = self.datadir / "out"
        dstdir.mkdir()

        dstfile = dstdir / self.srcfile.name
        self.assertFalse(dstfile.exists())

        url = self.srcfile.as_uri()
        geomodels.data.download(url, dstdir, progress=False)

        self.assertTrue(dstfile.exists())
        with open(dstfile) as fd:
            data = fd.read()

        self.assertEqual(data, self.DATA)

    @unittest.skipIf(
        not isinstance(pathlib.Path(), pathlib.PosixPath),
        reason="not on a posix platform.",
    )
    def test_download_file(self):
        dstdir = self.datadir / "out"
        dstdir.mkdir()

        dstfile = dstdir / self.srcfile.name
        self.assertFalse(dstfile.exists())

        url = str(self.srcfile)
        geomodels.data.download(url, dstdir, progress=False)

        self.assertTrue(dstfile.exists())
        with open(dstfile) as fd:
            data = fd.read()

        self.assertEqual(data, self.DATA)


class InstallTestCase(unittest.TestCase):
    MODEL_TYPES = [
        geomodels.data.EGeoidModel,
        geomodels.data.EGravityModel,
        geomodels.data.EMagneticModel,
    ]

    def setUp(self) -> None:
        self.download_patcher = mock.patch(
            "geomodels.data.download", return_value="dummy"
        )
        self.unpack_archive_patcher = mock.patch("shutil.unpack_archive")
        self.download_mock = self.download_patcher.start()
        self.unpack_archive_mock = self.unpack_archive_patcher.start()

    def tearDown(self) -> None:
        self.download_patcher.stop()
        self.unpack_archive_patcher.stop()

    def test_install_one_model(self):
        model = geomodels.data.EGravityModel.EGM96
        url = geomodels.data.get_model_url(model)

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        self.download_mock.assert_called_once_with(
            url, mock.ANY, progress=False
        )
        self.unpack_archive_mock.assert_called_once_with(
            mock.ANY, extract_dir=datadir
        )

    def test_install_one_model_type(self):
        model = geomodels.data.EModelType.GRAVITY
        n_models = len(geomodels.data.EGravityModel)

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_all_models(self):
        model = geomodels.data.EModelGroup.ALL

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        n_models = sum(len(m) for m in self.MODEL_TYPES)
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_minimal_models(self):
        model = geomodels.data.EModelGroup.MINIMAL

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        n_models = 3
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_recommended_models(self):
        model = geomodels.data.EModelGroup.RECOMMENDED

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        self.download_mock.assert_called()
        self.assertGreaterEqual(self.download_mock.call_count, 3)
        self.assertLessEqual(self.download_mock.call_count, 7)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertGreaterEqual(self.unpack_archive_mock.call_count, 3)
        self.assertLessEqual(self.unpack_archive_mock.call_count, 7)

    def test_install_geoid_models(self):
        model = geomodels.data.EModelType.GEOID

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        n_models = len(geomodels.data.EGeoidModel)
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertGreaterEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_gravity_models(self):
        model = geomodels.data.EModelType.GRAVITY

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        n_models = len(geomodels.data.EGravityModel)
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertGreaterEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_magnetic_models(self):
        model = geomodels.data.EModelType.MAGNETIC

        with tempfile.TemporaryDirectory() as datadir:
            geomodels.data.install(model, datadir, progress=False)

        n_models = len(geomodels.data.EMagneticModel)
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertGreaterEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_skip(self):
        datadir = geomodels.data.get_default_data_path()
        model = geomodels.data.EMagneticModel.IGRF12

        geomodels.data.install(model, datadir, progress=False)

        self.download_mock.assert_not_called()
        self.unpack_archive_mock.assert_not_called()

    def test_install_skip_one(self):
        model = geomodels.data.EModelType.MAGNETIC

        with tempfile.TemporaryDirectory() as datadir:
            model_dir = pathlib.Path(datadir) / model.value
            model_dir.mkdir()

            igrf12 = geomodels.data.EMagneticModel.IGRF12
            model_file = model_dir / (igrf12.name.lower() + ".dummyext")
            open(model_file, "w").close()  # touch

            geomodels.data.install(model, datadir, progress=False)

        expected_call_count = len(geomodels.data.EMagneticModel) - 1
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, expected_call_count)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir
        )
        self.assertEqual(
            self.unpack_archive_mock.call_count, expected_call_count
        )

    def test_install_invalid_01(self):
        model = None

        with tempfile.TemporaryDirectory() as datadir:
            self.assertRaises(
                (TypeError, ValueError),
                geomodels.data.install,
                model,
                datadir,
                progress=False,
            )
