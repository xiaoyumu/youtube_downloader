import os
import unittest


class UtilTest(unittest.TestCase):
    def test_file_name(self):
        actual = os.path.basename("D:\\test\\file.mp4")
        actual = actual.split(".")[0]
        expected = "file"

        self.assertEqual(expected, actual)
