import unittest
import helpers as helpers

"""Unit tests for helper code"""


class TestHelpers(unittest.TestCase):
    def test_to_microsecs(self):
        self.assertEqual(helpers.to_microsecs("00:00:00"), 0)
        self.assertEqual(helpers.to_microsecs("00:00:01"), 1000000)
        self.assertEqual(helpers.to_microsecs("99:59:59"), 359999000000)

        self.assertRaises(ValueError, helpers.to_microsecs, "00:00:0")
        self.assertRaises(ValueError, helpers.to_microsecs, "-00:00:0")
        self.assertRaises(ValueError, helpers.to_microsecs, "0:00:00")
        self.assertRaises(ValueError, helpers.to_microsecs, "00:0:00")
        self.assertRaises(ValueError, helpers.to_microsecs, "00:00:00:00")
        self.assertRaises(ValueError, helpers.to_microsecs, "99:99:99")
        self.assertRaises(ValueError, helpers.to_microsecs, "19:59:99")
        self.assertRaises(ValueError, helpers.to_microsecs, "19:99:59")
        self.assertRaises(ValueError, helpers.to_microsecs, "100:59:59")
        self.assertRaises(ValueError, helpers.to_microsecs, "00:0")
        self.assertRaises(ValueError, helpers.to_microsecs, "adfds")
        self.assertRaises(TypeError, helpers.to_microsecs, 1)

    def test_to_HHMMSS(self):
        self.assertEqual(helpers.to_HHMMSS(0), "00:00:00")
        self.assertEqual(helpers.to_HHMMSS(1), "00:00:00")
        self.assertEqual(helpers.to_HHMMSS(100000), "00:00:00")
        self.assertEqual(helpers.to_HHMMSS(100000), "00:00:00")
        self.assertEqual(helpers.to_HHMMSS(1000000), "00:00:01")
        self.assertEqual(helpers.to_HHMMSS(359999000000), "99:59:59")
        self.assertEqual(helpers.to_HHMMSS(1), "00:00:00")

        self.assertRaises(ValueError, helpers.to_HHMMSS, 359999000001)
        self.assertRaises(TypeError, helpers.to_HHMMSS, "adfds")
