# -*- coding: utf-8 -*-

import re
import unittest

import geomodels


class GeographicLibCommonCase(unittest.TestCase):
    def test_lib_version_str(self):
        version = geomodels.lib_version_str()
        self.assertIsInstance(version, str)
        self.assertRegex(version, r'\d+\.\d+(\.\d+)?')

    def test_lib_version_info(self):
        info = geomodels.lib_version_info()
        self.assertIsInstance(info, tuple)
        self.assertEqual(len(info), 3)
        self.assertEqual(info, (info.major, info.minor, info.micro))
        self.assertIsInstance(info.major, int)
        self.assertIsInstance(info.minor, int)
        self.assertIsInstance(info.micro, int)

    def test_version_consistency(self):
        version_str = geomodels.lib_version_str()
        version_info = geomodels.lib_version_info()

        mobj = re.match(
            r'(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<micro>\d+))?', version_str)

        self.assertEqual(version_info.major, int(mobj.group('major')))
        self.assertEqual(version_info.minor, int(mobj.group('minor')))
        if mobj.group('micro'):
            self.assertEqual(version_info.micro, int(mobj.group('micro')))


if __name__ == '__main__':
    unittest.main()
