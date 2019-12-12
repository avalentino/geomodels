# -*- coding: utf-8 -*-

import os
import unittest

import geomodels.data


class DataPathTestCase(unittest.TestCase):
    def test_default_data_path(self):
        path = geomodels.data.get_default_data_path()
        self.assertTrue(os.path.exists(path))

    def test_default_data_path_from_env(self):
        old_env = os.environ.get('GEOGRAPHICLIB_DATA')
        dummy_path = '/dummy/path'
        os.environ['GEOGRAPHICLIB_DATA'] = dummy_path

        try:
            path = geomodels.data.get_default_data_path()
            self.assertEqual(path, dummy_path)
        finally:
            if old_env is None:
                del os.environ['GEOGRAPHICLIB_DATA']
            else:
                os.environ['GEOGRAPHICLIB_DATA'] = old_env


if __name__ == '__main__':
    unittest.main()
