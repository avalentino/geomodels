# -*- coding: utf-8 -*-

import io
import re
import sys
import pathlib
import tempfile
import unittest
import subprocess

from unittest import mock
from contextlib import redirect_stdout

from geomodels import cli
from geomodels import get_default_data_path
from geomodels import __package__ as PKG, __version__ as VERSION

import geomodels.data


def _make_cmd(*args):
    return [sys.executable, '-m', PKG] + list(args)


class MainTestCase(unittest.TestCase):
    def test_version(self):
        cmd = _make_cmd('--version')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        self.assertIn(VERSION, result.stdout)

    def test_help(self):
        cmd = _make_cmd('--help')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)

    def test_h(self):
        cmd = _make_cmd('-h')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)


class InfoSubCommandTestCase(unittest.TestCase):
    VERSION_RE = re.compile(fr'^geomodels version:\s+{VERSION}$', re.MULTILINE)
    DATAPATH_RE = re.compile(
        r'^data directory:\s+{!r}$'.format(get_default_data_path()),
        re.MULTILINE)

    def test_help(self):
        cmd = _make_cmd('info', '--help')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('info', usage)

    def test_h(self):
        cmd = _make_cmd('info', '-h')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('info', usage)

    def test_default(self):
        with redirect_stdout(io.StringIO()) as sout:
            ret = cli.main('info')
        self.assertEqual(ret, None)
        output = sout.getvalue()
        self.assertRegex(output, self.VERSION_RE)
        self.assertNotRegex(output, self.DATAPATH_RE)

    def test_data(self):
        with redirect_stdout(io.StringIO()) as sout:
            ret = cli.main('info', '--data')
        self.assertEqual(ret, None)
        output = sout.getvalue()
        self.assertNotRegex(output, self.VERSION_RE)
        self.assertRegex(output, self.DATAPATH_RE)

    def test_all(self):
        with redirect_stdout(io.StringIO()) as sout:
            ret = cli.main('info', '--all')
        self.assertEqual(ret, None)
        output = sout.getvalue()
        self.assertRegex(output, self.VERSION_RE)
        self.assertRegex(output, self.DATAPATH_RE)


class InstallDataSubCommandTestCase(unittest.TestCase):
    MODEL_TYPES = [
        geomodels.data.EGeoidModel,
        geomodels.data.EGravityModel,
        geomodels.data.EMagneticModel,
    ]

    def setUp(self) -> None:
        self.download_patcher = mock.patch(
            'geomodels.data.download', return_value='dummy')
        self.unpack_archive_patcher = mock.patch('shutil.unpack_archive')
        self.download_mock = self.download_patcher.start()
        self.unpack_archive_mock = self.unpack_archive_patcher.start()

    def tearDown(self) -> None:
        self.download_patcher.stop()
        self.unpack_archive_patcher.stop()

    def test_help(self):
        cmd = _make_cmd('install-data', '--help')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('install-data', usage)

    def test_h(self):
        cmd = _make_cmd('install-data', '-h')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('install-data', usage)

    def test_install_all_models(self):
        model = geomodels.data.EModelGroup.ALL

        with tempfile.TemporaryDirectory() as datadir:
            ret = cli.main(
                'install-data', '-d', datadir, '--no-progress', model.value)

        self.assertEqual(ret, None)

        n_models = sum(len(m) for m in self.MODEL_TYPES)
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir)
        self.assertEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_minimal_models(self):
        model = geomodels.data.EModelGroup.MINIMAL

        with tempfile.TemporaryDirectory() as datadir:
            ret = cli.main(
                'install-data', '-d', datadir, '--no-progress', model.value)

        self.assertEqual(ret, None)

        n_models = 3
        self.download_mock.assert_called()
        self.assertEqual(self.download_mock.call_count, n_models)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir)
        self.assertEqual(self.unpack_archive_mock.call_count, n_models)

    def test_install_recommended_models(self):
        model = geomodels.data.EModelGroup.RECOMMENDED

        with tempfile.TemporaryDirectory() as datadir:
            ret = cli.main(
                'install-data', '-d', datadir, '--no-progress', model.value)

        self.assertEqual(ret, None)
        self.download_mock.assert_called()
        self.assertGreaterEqual(self.download_mock.call_count, 3)
        self.assertLessEqual(self.download_mock.call_count, 7)
        self.unpack_archive_mock.assert_called_with(
            mock.ANY, extract_dir=datadir)
        self.assertGreaterEqual(self.unpack_archive_mock.call_count, 3)
        self.assertLessEqual(self.unpack_archive_mock.call_count, 7)


class ImportIgrfSubCommandTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.wmmdata_mock = mock.Mock()
        self.import_igrf_patcher = mock.patch(
            'geomodels.cli.import_igrf_txt', return_value=self.wmmdata_mock)
        self.import_igrf_mock = self.import_igrf_patcher.start()

    def tearDown(self) -> None:
        self.import_igrf_patcher.stop()

    def test_help(self):
        cmd = _make_cmd('import-igrf', '--help')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('import-igrf', usage)

    def test_h(self):
        cmd = _make_cmd('import-igrf', '-h')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('import-igrf', usage)

    def test_import_igrf_file(self):
        path = pathlib.Path(__file__).parent / 'data' / 'igrf12coeffs.txt'
        with tempfile.TemporaryDirectory() as outpath:
            cli.main('import-igrf', '-o', outpath, str(path))

        self.import_igrf_mock.assert_called_once_with(str(path))
        self.wmmdata_mock.save.assert_called_once_with(outpath, False)


class TestSubCommandTestCase(unittest.TestCase):
    def test_help(self):
        cmd = _make_cmd('test', '--help')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('test', usage)

    def test_h(self):
        cmd = _make_cmd('test', '-h')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        usage = result.stdout.splitlines()[0]
        self.assertIn('usage:', usage)
        self.assertIn(cli.PROG, usage)
        self.assertIn('test', usage)


if __name__ == '__main__':
    unittest.main()
