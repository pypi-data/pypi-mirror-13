"""Utility functions for pylinac."""
import decimal
import inspect
import os.path as osp
from collections import Iterable

import numpy as np

from .io import is_valid_file


def is_close(val, target, delta=1):
    """Return whether the value is near the target value."""
    try:
        targets = (value for value in target)
    except AttributeError:
        targets = [target]
    for target in targets:
        if (val < target + delta) and (val > target - delta):
            return True
    return False

def import_mpld3():
    """Try importing MPLD3. Raises error if not installed. Returns the MPLD3 library."""
    try:
        import mpld3
    except ImportError:
        raise ImportError("The MPLD3 library must be installed to make interactive plots. See http://mpld3.github.io/index.html for info.")
    return mpld3


def typed_property(name, expected_type_or_tuple_of_types):
    """Type-enforced property. Python Cookbook 9.21 (3rd ed)."""
    storage_name = '_' + name

    @property
    def prop(self):
        return getattr(self, storage_name, None)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type_or_tuple_of_types):
            raise TypeError("{} must be a {}. Got: {}".format(name, expected_type_or_tuple_of_types, type(value)))
        setattr(self, storage_name, value)

    return prop


def simple_round(number, decimals=0):
    """Round a number to the given number of decimals. Fixes small floating number errors."""
    num = int(round(number * 10 ** decimals))
    num /= 10 ** decimals
    return num


def is_dicom(file):
    """Boolean specifying if file is a proper DICOM file.

    This function is a pared down version of read_preamble meant for a fast return.
    The file is read for a proper preamble ('DICM'), returning True if so,
    and False otherwise. This is a conservative approach.

    Parameters
    ----------
    file : str
        The path to the file.

    See Also
    --------
    pydicom.filereader.read_preamble
    pydicom.filereader.read_partial
    """
    is_valid_file(file, raise_error=True)
    fp = open(file, 'rb')
    preamble = fp.read(0x80)
    prefix = fp.read(4)
    if prefix == b"DICM":
        return True
    else:
        return False


def isnumeric(object):
    """Check whether the passed object is numeric in any sense."""
    return isinstance(object, (int, float, decimal.Decimal, np.number))


def is_iterable(object):
    """Determine if an object is iterable."""
    if isinstance(object, Iterable):
        return True
    else:
        return False


def go_up_dirlevel(levels=0):
    """Go up directory levels from where the caller file is located.

    Parameters
    ----------
    levels : int
        Specifies how many levels to go up. 0 goes to the current directory.
    """
    calling_file = inspect.stack()[1][1]
    calling_dir = osp.dirname(calling_file)
    new_dir = calling_dir
    while levels > 0:
        old_dir = new_dir
        new_dir = osp.dirname(old_dir)
        levels -= 1
    return new_dir

