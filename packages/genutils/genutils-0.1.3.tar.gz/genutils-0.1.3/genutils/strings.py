# coding=utf-8
"""
Some functions helping with string encoding and decoding.
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


def to_str(str_or_bytes, encoding='utf-8'):
    """Take argument and return as unicode string.

    :param str_or_bytes: argument to decode.
    :type str_or_bytes: str or bytes
    :param encoding: the encoding to use if argument is of type bytes
    :returns: argument as unicode string.
    :rtype: str
    """
    if isinstance(str_or_bytes, bytes):
        value = str_or_bytes.decode(encoding)
    else:
        value = str_or_bytes
    return value


def to_bytes(str_or_bytes, encoding='utf-8)'):
    """Take argument and return as bytes.

    :param str_or_bytes: argument to encode.
    :type str_or_bytes: str or bytes
    :param encoding: the encoding to use if argument is of type str
    :return: argument as bytes
    :rtype: bytes
    """
    if isinstance(str_or_bytes, str):
        value = str_or_bytes.encode(encoding)
    else:
        value = str_or_bytes
    return value
