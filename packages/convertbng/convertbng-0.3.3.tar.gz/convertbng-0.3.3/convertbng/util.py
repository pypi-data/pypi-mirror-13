# -*- coding: utf-8 -*-
"""
util.py

Created by Stephan Hügel on 2015-06-22

This file is part of convertbng.

The MIT License (MIT)

Copyright (c) 2015 Stephan Hügel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
from ctypes import cdll, c_double, Structure, c_void_p, cast, c_size_t, POINTER
from sys import platform
from array import array
import numpy as np
import os

if platform == "darwin":
    ext = "dylib"
else:
    ext = "so"

__author__ = u"Stephan Hügel"
__version__ = "0.3.3"

file_path = os.path.dirname(__file__)
lib = cdll.LoadLibrary(os.path.join(file_path, 'liblonlat_bng.' + ext))


class _FFIArray(Structure):
    """ Convert sequence of floats to a C-compatible void array """
    _fields_ = [("data", c_void_p),
                ("len", c_size_t)]

    @classmethod
    def from_param(cls, seq):
        """  Allow implicit conversions from a sequence of 64-bit floats."""
        return seq if isinstance(seq, cls) else cls(seq)

    def __init__(self, seq, data_type = c_double):
        """
        Convert sequence of values into array, then ctypes Structure

        Rather than checking types (bad), we just try to blam seq
        into a ctypes object using from_buffer. If that doesn't work,
        we try successively more conservative approaches:
        numpy array -> array.array -> read-only buffer -> CPython iterable
        """
        try:
            len(seq)
        except TypeError:
             # we've got an iterator or a generator, so consume it
            seq = array('d', seq)
        array_type = data_type * len(seq)
        try:
            raw_seq = array_type.from_buffer(seq.astype(np.float64))
        except (TypeError, AttributeError):
            try:
                raw_seq = array_type.from_buffer_copy(seq.astype(np.float64))
            except (TypeError, AttributeError):
                # it's a list or a tuple
                raw_seq = array_type.from_buffer(array('d', seq))
        self.data = cast(raw_seq, c_void_p)
        self.len = len(seq)


class _Result_Tuple(Structure):
    """ Container for returned FFI data """
    _fields_ = [("e", _FFIArray),
                ("n", _FFIArray)]


def _void_array_to_list(restuple, _func, _args):
    """ Convert the FFI result to Python data structures """
    eastings = POINTER(c_double * restuple.e.len).from_buffer_copy(restuple.e)[0]
    northings = POINTER(c_double * restuple.n.len).from_buffer_copy(restuple.n)[0]
    res_list = [list(eastings), list(northings)]
    drop_array(restuple.e, restuple.n)
    return res_list


# Multi-threaded FFI functions
convert_bng = lib.convert_to_bng_threaded
convert_bng.argtypes = (_FFIArray, _FFIArray)
convert_bng.restype = _Result_Tuple
convert_bng.errcheck = _void_array_to_list

convert_lonlat = lib.convert_to_lonlat_threaded
convert_lonlat.argtypes = (_FFIArray, _FFIArray)
convert_lonlat.restype = _Result_Tuple
convert_lonlat.errcheck = _void_array_to_list

convert_to_osgb36_threaded = lib.convert_to_osgb36_threaded
convert_to_osgb36_threaded.argtypes = (_FFIArray, _FFIArray)
convert_to_osgb36_threaded.restype = _Result_Tuple
convert_to_osgb36_threaded.errcheck = _void_array_to_list

convert_osgb36_to_ll = lib.convert_osgb36_to_ll_threaded
convert_osgb36_to_ll.argtypes = (_FFIArray, _FFIArray)
convert_osgb36_to_ll.restype = _Result_Tuple
convert_osgb36_to_ll.errcheck = _void_array_to_list

convert_etrs89_en_to_osgb36 = lib.convert_etrs89_to_osgb36_threaded
convert_etrs89_en_to_osgb36.argtypes = (_FFIArray, _FFIArray)
convert_etrs89_en_to_osgb36.restype = _Result_Tuple
convert_etrs89_en_to_osgb36.errcheck = _void_array_to_list

convert_osgb36_en_to_etrs89 = lib.convert_osgb36_to_etrs89_threaded
convert_osgb36_en_to_etrs89.argtypes = (_FFIArray, _FFIArray)
convert_osgb36_en_to_etrs89.restype = _Result_Tuple
convert_osgb36_en_to_etrs89.errcheck = _void_array_to_list

# Free FFI-allocated memory
drop_array = lib.drop_float_array
drop_array.argtypes = (_FFIArray, _FFIArray)
drop_array.restype = None

# The type checks are not exhaustive. I know.
def convertbng(lons, lats):
    """
    Multi-threaded lon, lat --> BNG conversion
    Returns a list of two lists containing Easting and Northing floats,
    respectively
    Uses the Helmert transform
    """
    if isinstance(lons, float):
        lons = [lons]
        lats = [lats]
    return convert_bng(lons, lats)

def convertlonlat(eastings, northings):
    """
    Multi-threaded BNG --> lon, lat conversion
    Returns a list of two lists containing Longitude and Latitude floats,
    respectively
    Uses the Helmert transform
    """
    if isinstance(eastings, (int, long)):
        eastings = [eastings]
        northings = [northings]
    return convert_lonlat(eastings, northings)

def convert_osgb36(lons, lats):
    """
    Multi-threaded lon, lat --> OSGB36 conversion, using OSTN02 data
    Returns a list of two lists containing Easting and Northing floats,
    respectively
    """
    if isinstance(lons, float):
        lons = [lons]
        lats = [lats]
    return convert_to_osgb36_threaded(lons, lats)

def convert_osgb36_to_lonlat(eastings, northings):
    """
    Multi-threaded OSGB36 --> Lon, Lat conversion, using OSTN02 data
    Returns a list of two lists containing Easting and Northing floats,
    respectively
    """
    if isinstance(eastings, float):
        eastings = [eastings]
        northings = [northings]
    return convert_osgb36_to_ll(eastings, northings)

def convert_etrs89_to_osgb36(eastings, northings):
    """
    Multi-threaded ETRS89 Eastings and Northings --> OSGB36 conversion, using OSTN02 data
    Returns a list of two lists containing Easting and Northing floats,
    respectively
    """
    if isinstance(eastings, float):
        eastings = [eastings]
        northings = [northings]
    return convert_etrs89_en_to_osgb36(eastings, northings)

def convert_osgb36_to_etrs89(eastings, northings):
    """
    Multi-threaded OSGB36 Eastings and Northings --> ETRS89 Eastings and Northings conversion,
    using OSTN02 data
    Returns a list of two lists containing Easting and Northing floats,
    respectively
    """
    if isinstance(eastings, float):
        eastings = [eastings]
        northings = [northings]
    return convert_osgb36_en_to_etrs89(eastings, northings)
