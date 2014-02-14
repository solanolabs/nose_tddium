# -*- coding: utf-8

from cStringIO import StringIO
import sys
import unittest

import nose_tddium

class TestUnicodeConversion(unittest.TestCase):

    def setUp(self):
        self.orig_stdout = sys.stdout
        sys.stdout = nose_tddium.Tee(StringIO(), sys.stdout)

    def tearDown(self):
        sys.stdout = self.orig_stdout

    def test_patterns_stdout(self):
        "Unicode patterns should not produce errors"
        print >> sys.stdout, u'\u55ae\u8eca' # Big5
        print >> sys.stdout, u'\u8fd9\u662f\u4e2d\u6587\u6d4b\u8bd5\uff01' # GB2312
        print >> sys.stdout, u'\u044f\u2248\u043f\u2564\u043f\u255f\u043f\u2568' # KOI8-R
        print >> sys.stdout, u'\u0421\u2014\u0420\xb6\u0420\xb0\u0420\u0454' # Windows-1251
        sys.stdout.flush()

if __name__ == '__main__':
    unittest.main()
