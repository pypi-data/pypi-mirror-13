# Copyright 2016 United Kingdom Atomic Energy Authority (UKAEA)
#
# This file is part of IDLBridge.
#
# IDLBridge is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# IDLBridge is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IDLBridge. If not, see <http://www.gnu.org/licenses/>.

"""
Allows users to call IDL routines from inside Python.

This package wraps the IDL callable library and provides a simple user interface
for passing data between IDL and Python. IDL functions and procedures can be
exposed in Python and be called like native Python functions.
"""

import ctypes as _ctypes
from . import _core

__author__ = 'Dr. Alex Meakins'
__responsible_officer__ = 'Dr. Alex Meakins'
__version__ = "1.1.0"

# By default the core (IDL) library is opened by Python with RTLD_LOCAL
# preventing subsequently loaded IDL DLM libraries from seeing the IDL_*
# symbols. To solve this we reload the library with RTLD_GLOBAL prior to
# its first use.
_ctypes.CDLL(_core.__file__, mode=_ctypes.RTLD_GLOBAL)

# module level bridge and functions
__bridge__ = _core.IDLBridge()


def execute(command):
    """
    Executes a string as an IDL command.

    :param command: A string defining the idl command e.g. "d = 5.1"
    :return: None
    """

    global __bridge__
    __bridge__.execute(command)


def get(variable):
    """
    Returns a Python copy of the specified IDL variable.

    :param variable: A string containing the variable name.
    :return: The IDL variable data converted to an appropriate Python type.
    """

    global __bridge__
    return __bridge__.get(variable)


def put(variable, data):
    """
    Sets an IDL variable with Python data.

    :param variable: A string containing the variable name.
    :param data: A Python object containing data to send.
    """

    global __bridge__
    __bridge__.put(variable, data)


def delete(variable):
    """
    Deletes the specified IDL variable.

    :param variable: A string specifying the name of the IDL variable to delete.
    :return: None
    """

    global __bridge__
    __bridge__.delete(variable)


def export_function(name, return_arguments=None):
    """
    Wraps an IDL function in an object that behaves like a Python function.

    For example, to gain access to the IDL "sin" function type:

        sin = idl.export_function("sin")

    Use "sin" like an ordinary Python function:

        v = sin(0.5)

    Keyword arguments are specified using the normal Python syntax. To provide
    an IDL "/keyword", simply set the keyword equal to True in Python.

        my_idl_function(1.2, 3.4, my_keyword=True)

    IDL supports pass by reference, which allows the function to modify the
    value of variables supplied to the function. Python does not support
    pass by reference. To provide access to modified arguments, a
    return_arguments parameter is provided. The return_arguments parameter
    expects a list of indices, corresponding to the location of the
    argument to return. Selected arguments will be packed into a tuple
    with the return value and returned by the function.

    For example:

        my_func = idl.export_function("my_func", returned_arguments=[0, 3])

    specifies that the first argument and the fourth argument are to be
    returned along with the return value i.e. my_func will return a tuple
    containing:

        (return_value, argument_0, argument_3)

    This means it is possible to call the IDL function like a similarly
    defined Python function:

        v, a, d = my_func(a, b, c, d, e)

    If any arguments specified for return are not used due to being optional
    arguments, the unset arguments will not be returned.

    For example:

        v, a = my_func(a, b)

    Here argument d is not set, so it is not returned.

    :param name: A string specifying the name of the IDL function to wrap.
    :param return_arguments: A list object containing the index of
    arguments to return.
    :return: An IDLFunction object.
    """

    global __bridge__
    return __bridge__.export_function(name, return_arguments)


def export_procedure(name, return_arguments=None):
    """
    Wraps an IDL procedure in an object that behaves like a Python function.

    For example, to gain access to the IDL "plot" procedure type:

        plot = idl.export_procedure("plot")

    Use "plot" like an ordinary Python function:

        plot([1,2,3], [4,5,6])

    Keyword arguments are specified using the normal Python syntax. To provide
    an IDL "/keyword", simply set the keyword equal to True in Python.

        my_idl_procedure(1.2, 3.4, my_keyword=True)

    IDL supports pass by reference, which allows the procedure to modify the
    value of variables supplied to the procedure. Python does not support
    pass by reference. To provide access to modified arguments, a
    return_arguments parameter is provided. The return_arguments parameter
    expects a list of indices, corresponding to the location of the
    argument to return. Selected arguments will be packed into a tuple
    and returned by the procedure.

    For example:

        my_pro = idl.export_procedure("my_pro", returned_arguments=[0, 3])

    specifies that the first argument and the fourth argument are to be
    returned i.e. my_pro will return a tuple containing:

        (argument_0, argument_3)

    This means it is possible to call the IDL procedure like a similarly
    defined Python function:

        a, d = my_pro(a, b, c, d, e)

    If any arguments specified for return are not used due to being optional
    arguments, the unset arguments will not be returned.

    For example:

        a = my_pro(a, b)

    Here argument d is not set, so it is not returned.

    :param None: A string specifying the name of the IDL procedure to wrap.
    :param return_arguments: A list object containing the index of
    arguments to return.
    :return: An IDLProcedure object.
    """

    global __bridge__
    return __bridge__.export_procedure(name, return_arguments)
