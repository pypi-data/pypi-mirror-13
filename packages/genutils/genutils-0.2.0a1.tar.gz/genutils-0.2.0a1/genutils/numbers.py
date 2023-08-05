# coding=utf-8
"""
Some utilities related to numbers.
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


def is_even(num):
    """Is num even?

    :param num: number to check.
    :type num: int
    :returns: True if num is even.
    :rtype: boolean
    :raises: ``TypeError`` if num is not an int.
    """
    if not isinstance(num, int):
        raise TypeError("{} is not an int".format(num))
    return num % 2 == 0


def is_odd(num):
    """Is num odd?

    :param num: number to check.
    :type num: int
    :returns: True if num is odd.
    :rtype: boolean
    :raises: ``TypeError`` if num is not an int.
    """
    if not isinstance(num, int):
        raise TypeError("{} is not an int".format(num))
    return num % 2 == 1
