# coding=utf-8
"""
Tasts for encodings.
"""
# Copyright (c) 2015 Stefan Braun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import unittest

import genutils.strings.encodings as enc


class EncodingsTest(unittest.TestCase):
    def test_to_str_bytes(self):
        val = bytes('äüß', encoding='utf-8')
        self.assertIsInstance(val, bytes)
        res = enc.to_str(val)
        self.assertIsInstance(res, str)

    def test_to_str_bytes_latin(self):
        val = bytes('äüß', encoding='latin-1')
        self.assertIsInstance(val, bytes)
        res = enc.to_str(val, encoding='latin-1')
        self.assertIsInstance(res, str)

    def test_to_str_str(self):
        val = 'öüä'
        self.assertIsInstance(val, str)
        res = enc.to_str(val)
        self.assertIsInstance(res, str)

    def test_to_bytes_bytes(self):
        val = bytes('äüß', encoding='utf-8')
        self.assertIsInstance(val, bytes)
        res = enc.to_bytes(val)
        self.assertIsInstance(res, bytes)

    def test_to_bytes_bytes_latin(self):
        val = bytes('äüß', encoding='latin-1')
        self.assertIsInstance(val, bytes)
        res = enc.to_bytes(val)
        self.assertIsInstance(res, bytes)

    def test_to_bytes_str(self):
        val = 'äüö'
        self.assertIsInstance(val, str)
        res = enc.to_bytes(val)
        self.assertIsInstance(res, bytes)
        valb = bytes('äüö', encoding='utf-8')
        self.assertEqual(valb, res)

    def test_to_bytes_str_latin(self):
        val = 'äüö'
        self.assertIsInstance(val, str)
        res = enc.to_bytes(val, encoding='latin-1')
        self.assertIsInstance(res, bytes)
        valb = bytes('äüö', encoding='latin-1')
        self.assertEqual(valb, res)
