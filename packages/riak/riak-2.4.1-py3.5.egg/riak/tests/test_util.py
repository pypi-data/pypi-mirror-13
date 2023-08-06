import platform

from riak.util import is_timeseries_supported

if platform.python_version() < '2.7':
    unittest = __import__('unittest2')
else:
    import unittest


class UtilUnitTests(unittest.TestCase):
    def test_is_timeseries_supported(self):
        v = (2, 7, 11)
        self.assertEqual(True, is_timeseries_supported(v))
        v = (2, 7, 12)
        self.assertEqual(True, is_timeseries_supported(v))
        v = (3, 3, 6)
        self.assertEqual(False, is_timeseries_supported(v))
        v = (3, 4, 3)
        self.assertEqual(False, is_timeseries_supported(v))
