# cython: language_level=3

from libc.math cimport isnan, isfinite
from cpython cimport PyList_Check, PyDict_Check

from jsonata import jexception

cdef object NULL_VALUE = None  # Placeholder; replaced with a proper NullValue class below
cdef object NONE = object()


# ------------------------
# NullValue Representation
# ------------------------

cdef class NullValue:
    def __repr__(self):
        return "null"

NULL_VALUE = NullValue()


# ------------------------
# JList Implementation
# ------------------------

cdef class JList:
    cdef public list data
    cdef public bint sequence
    cdef public bint outer_wrapper
    cdef public bint tuple_stream
    cdef public bint keep_singleton
    cdef public bint cons

    def __cinit__(self, object seq=None):
        if seq is None:
            self.data = []
        else:
            self.data = list(seq)
        self.sequence = False
        self.outer_wrapper = False
        self.tuple_stream = False
        self.keep_singleton = False
        self.cons = False

    def __getitem__(self, int idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def append(self, object val):
        self.data.append(val)

    def __repr__(self):
        return f"JList({self.data})"


# ------------------------
# RangeList Implementation
# ------------------------

cdef class RangeList:
    cdef int a, b, size

    def __init__(self, int left, int right):
        self.a = left
        self.b = right
        self.size = right - left + 1

    def __len__(self):
        return self.size

    def __getitem__(self, int index):
        if index < 0 or index >= self.size:
            raise IndexError(index)
        return convert_number(self.a + index)

    def __iter__(self):
        cdef int i
        for i in range(self.a, self.b + 1):
            yield convert_number(i)


# ------------------------
# Core Utility Functions
# ------------------------

cpdef bint is_numeric(object v):
    """
    Fast numeric check using C math functions.
    Returns True if v is int or finite float.
    """
    if isinstance(v, bool):
        return False
    elif isinstance(v, int):
        return True
    elif isinstance(v, float):
        if isnan(<double>v):
            return False
        if not isfinite(<double>v):
            raise jexception.JException("D1001", 0, v)
        return True
    return False


cpdef bint is_array_of_numbers(object v):
    """
    Checks if list consists only of numbers
    """
    if isinstance(v, list):
        for o in v:
            if not is_numeric(o):
                return False
        return True
    return False


cpdef bint is_array_of_strings(object v):
    """
    Checks if list consists only of strings
    """
    if isinstance(v, list):
        for o in v:
            if not isinstance(o, str):
                return False
        return True
    return False


cpdef object convert_number(double n):
    """
    Returns int if possible, else float
    """
    if not isfinite(n) or isnan(n):
        return None
    cdef long long_v = <long>n
    if n == long_v:
        return long_v
    return n


cpdef object convert_value(object val):
    return val if val is not NULL_VALUE else None


cpdef void recurse(object val):
    if isinstance(val, dict):
        convert_dict_nulls(val)
    elif isinstance(val, list):
        convert_list_nulls(val)


cpdef void convert_dict_nulls(dict res):
    cdef object key, val, new_val
    for key in list(res.keys()):
        val = res[key]
        new_val = convert_value(val)
        if new_val is not val:
            res[key] = new_val
        recurse(val)


cpdef void convert_list_nulls(list res):
    cdef Py_ssize_t i, n = len(res)
    cdef object val, new_val
    for i in range(n):
        val = res[i]
        new_val = convert_value(val)
        if new_val is not val:
            res[i] = new_val
        recurse(val)


# ------------------------
# Sequence Creation
# ------------------------

cpdef JList create_sequence(object el=NONE):
    cdef JList sequence
    if el is not NONE:
        if isinstance(el, list) and len(el) == 1:
            sequence = JList(el)
        else:
            sequence = JList([el])
    else:
        sequence = JList()
    sequence.sequence = True
    return sequence


cpdef JList create_sequence_from_iter(object it):
    sequence = JList(it)
    sequence.sequence = True
    return sequence


cpdef bint is_sequence(object result):
    return isinstance(result, JList) and result.sequence
