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

from libc.string cimport memcpy
import numpy as np
cimport numpy as np

# include IDL callable interface
include "idl_export.pxi"

# initialise numpy c-api
np.import_array()


class IDLLibraryError(Exception):
    """
    An IDL Library Error Exception.

    This exception is thrown when there is a problem interacting with the IDL
    callable library.
    """

    pass


class IDLTypeError(TypeError):
    """
    An IDL Type Error Exception.

    This exception is thrown when a data type is passed to the IDL library that
    it is unable to handle.
    """
    pass


class IDLValueError(ValueError):
    """
    An IDL Value Error Exception.

    This exception is thrown when a value is passed to the IDL library that it
    is unable to handle.
    """

    pass


# global variables used to track the usage of the IDL library
cdef:
    int __references__ = 0
    bint __shutdown__ = False


cdef _initialise_idl(bint quiet=True):
    """
    Initialise the IDL library.
    """

    cdef IDL_INIT_DATA init_data
    global __shutdown__
    if not __shutdown__:

        # initialise the IDL library
        init_data.options = IDL_INIT_NOCMDLINE #IDL_INIT_BACKGROUND
        if quiet:
            init_data.options |= IDL_INIT_QUIET
        v = IDL_Initialize(&init_data)

        # We have encountered an odd issue with IDL where it occasionally consumes (without executing) the first command
        # it is sent. This occurs whenever the user sets a IDL_STARTUP environment variable to point to an idl startup
        # script. The cause of this is unknown. To prevent this being a problem for the users we execute a null command
        # when the IDL library is initialised.
        IDL_ExecuteStr("MESSAGE, /RESET")

    else:

        # library has already been cleaned up, it can not be reinitialised
        raise IDLLibraryError("The IDL library has been shutdown, it cannot be restarted in this session.")


cdef _cleanup_idl():
    """
    Shutdown and clean-up the IDL library.
    """

    global __shutdown__
    if not __shutdown__:
        IDL_Cleanup(True)


cdef _register():
    """
    Registers a user of the IDL library.

    The IDL library is initialised when the first user registers.
    """

    global __references__
    global __shutdown__
    if __references__ == 0:
        _initialise_idl()
    __references__ += 1


cdef _deregister():
    """
    De-registers a user of the IDL library.

    The IDL library is shutdown when all users of the library are de-registered.
    """

    global __references__
    global __shutdown__
    __references__ -= 1
    if __references__ <= 0:
        _cleanup_idl()


cdef class IDLBridge:
    """
    Implements a bridge between the IDL library and Python.
    """

    def __init__(self):

        # register this bridge with the IDL library
        _register()

    def __dealloc__(self):

        # de-register this bridge with the IDL library
        _deregister()

    cpdef object execute(self, str command):
        """
        Executes a string as an IDL command.

        :param command: A string defining the idl command e.g. "d = 5.1"
        :return: None
        """

        byte_string = command.encode("UTF8")
        IDL_ExecuteStr(byte_string)

    cpdef object get(self, str variable):
        """
        Returns a python copy of the specified IDL variable.

        :param variable: A string containing the variable name.
        :return: The IDL variable data converted to python form.
        """

        cdef IDL_VPTR vptr

        # convert unicode string to c compatible byte string
        byte_string = variable.encode("UTF8")

        # request variable from IDL
        vptr = IDL_FindNamedVariable(byte_string, False)

        if vptr == NULL or vptr.type == IDL_TYP_UNDEF:
            raise IDLValueError("IDL Variable {} not found.".format(variable.upper()))

        # decode and return the IDL_Variable
        return self._get(vptr)

    cdef object _get(self, IDL_VPTR vptr):
        """
        Converts an IDL variable to a python variable.

        :param variable: A valid IDL_VPTR
        :return: The IDL variable data converted to python form.
        """

        # identify variable type and translate to python
        if vptr.flags & IDL_V_ARR:
            if vptr.flags & IDL_V_STRUCT:
                return self._get_structure(vptr)
            else:
                return self._get_array(vptr)
        elif vptr.type == IDL_TYP_BYTE: return vptr.value.c
        elif vptr.type == IDL_TYP_INT: return vptr.value.i
        elif vptr.type == IDL_TYP_UINT: return vptr.value.ui
        elif vptr.type == IDL_TYP_LONG: return vptr.value.l
        elif vptr.type == IDL_TYP_ULONG: return vptr.value.ul
        elif vptr.type == IDL_TYP_LONG64: return vptr.value.l64
        elif vptr.type == IDL_TYP_ULONG64: return vptr.value.ul64
        elif vptr.type == IDL_TYP_FLOAT: return vptr.value.f
        elif vptr.type == IDL_TYP_DOUBLE: return vptr.value.d
        elif vptr.type == IDL_TYP_COMPLEX: return complex(vptr.value.cmp.r, vptr.value.cmp.i)
        elif vptr.type == IDL_TYP_DCOMPLEX: return complex(vptr.value.dcmp.r, vptr.value.dcmp.i)
        elif vptr.type == IDL_TYP_STRING: return self._string_idl_to_py(vptr.value.str)
        elif vptr.type == IDL_TYP_PTR:
            return self._get_pointer(vptr)
        elif vptr.type == IDL_TYP_OBJREF:
            raise NotImplementedError("IDL object types are not supported.")
        else:
            raise IDLTypeError("Unrecognised IDL type.")

    cdef inline np.ndarray _get_array(self, IDL_VPTR vptr):
        """
        Converts an IDL array to an equivalent numpy array.

        :param vptr: An IDL variable pointer pointing to an IDL array definition.
        :return: A numpy array.
        """

        # All arrays MUST be copied otherwise changes in python or IDL will cause segfaults in one of the other

        # Different array types unfortunately need special handling.
        if vptr.type == IDL_TYP_STRING:
            return self._get_array_string(vptr)
        elif vptr.type == IDL_TYP_STRUCT:
            return self._get_array_structure(vptr)
        else:
            return self._get_array_scalar(vptr)

    cdef inline np.ndarray _get_array_string(self, IDL_VPTR vptr):
        """
        Converts an IDL string array to an equivalent numpy array.

        :param vptr: An IDL variable pointer pointing to an IDL string array definition.
        :return: A numpy array.
        """

        cdef:
            IDL_ARRAY *idl_array
            IDL_STRING idl_string
            list strings
            int index
            np.ndarray array
            np.npy_intp numpy_dimensions[IDL_MAX_ARRAY_DIM]
            np.PyArray_Dims new_dimensions

        # obtain IDL array structure from IDL variable
        idl_array = vptr.value.arr

        # The IDL string array is unpacked to form a flat list of strings, this is then
        # converted to a numpy array before finally being reshaped to the correct dimensions.

        # convert all the IDL strings in the array to python strings
        strings = []
        for index in range(idl_array.n_elts):

            # dereference idl string pointer
            idl_string = (<IDL_STRING *> (idl_array.data + index * idl_array.elt_len))[0]
            strings.append(self._string_idl_to_py(idl_string))

        # convert to a flat numpy array
        numpy_array = np.array(strings)

        # reshape array
        new_dimensions.len = idl_array.n_dim
        self._dimensions_idl_to_numpy(numpy_dimensions, idl_array.n_dim, idl_array.dim)
        new_dimensions.ptr = numpy_dimensions
        return np.PyArray_Newshape(numpy_array, &new_dimensions, np.NPY_CORDER)

    cdef inline np.ndarray _get_array_structure(self, IDL_VPTR vptr):

        raise NotImplementedError("Arrays of IDL structures are not supported.")

    cdef inline np.ndarray _get_array_scalar(self, IDL_VPTR vptr):
        """
        Converts an IDL scalar array to an equivalent numpy array.

        :param vptr: An IDL variable pointer pointing to an IDL scalar array definition.
        :return: A numpy array.
        """

        cdef:
            IDL_ARRAY *idl_array
            int num_dimensions
            np.npy_intp numpy_dimensions[IDL_MAX_ARRAY_DIM]
            np.ndarray numpy_array
            int index

        # obtain IDL array structure from IDL variable
        idl_array = vptr.value.arr

        # obtain numpy data type
        numpy_type = self._type_idl_to_numpy(vptr.type)

        # IDL defines its dimensions in the opposite order to numpy
        self._dimensions_idl_to_numpy(numpy_dimensions, idl_array.n_dim, idl_array.dim)

        # generate an empty numpy array and copy IDL array data
        numpy_array = np.PyArray_SimpleNew(idl_array.n_dim, numpy_dimensions, numpy_type)
        memcpy(numpy_array.data, <void *> idl_array.data, idl_array.arr_len)

        return numpy_array

    cdef inline dict _get_structure(self, IDL_VPTR vptr):
        """
        Converts an IDL structure a python dictionary.

        :param vptr: An IDL variable pointer pointing to an IDL structure definition.
        :return: A python dictionary.
        """

        cdef:
            str tag_name_bytes
            IDL_VPTR tag_vptr
            IDL_MEMINT tag_offset
            int index
            dict result

        result = {}

        # parse structure definition
        num_tags = IDL_StructNumTags(vptr.value.s.sdef)
        for index in range(num_tags):

            tag_name = IDL_StructTagNameByIndex(vptr.value.s.sdef, index, IDL_M_GENERIC, NULL).decode("UTF8").lower()
            tag_offset = IDL_StructTagInfoByIndex(vptr.value.s.sdef, index, IDL_M_GENERIC, &tag_vptr)

            # Populate IDL_VPTR value with data as it isn't actually set...!
            # (why idl doesn't do this itself I really don't know)
            if tag_vptr.flags & IDL_V_STRUCT:

                # structure
                tag_vptr.value.s.arr.data = <UCHAR *> (vptr.value.s.arr.data + tag_offset)

            elif tag_vptr.flags & IDL_V_ARR:

                # array
                tag_vptr.value.arr.data = <UCHAR *> (vptr.value.s.arr.data + tag_offset)

            else:

                # everything else
                tag_vptr.value = (<IDL_ALLTYPES *> (vptr.value.s.arr.data + tag_offset))[0]

            result[tag_name] = self._get(tag_vptr)

        return result

    cdef inline object _get_pointer(self, IDL_VPTR vptr):

        cdef:

            IDL_VPTR temp_vptr

        # The IDL c-api does not provide functions for handling pointer types, the documentation
        # says you must use user space tools. This is slow and horrible, thanks IDL developers <3.

        # Generate a unique temporary variable name.
        # To do this we store an id number in an IDL variable and increment it for each pointer handled
        # This code will fail if there are more temporary pointers than an unsigned long can uniquely
        # reference. I suspect IDL will fail long before that point.
        self.execute("if ~ isa(_idlbridge_pointer_count_) then _idlbridge_pointer_count_ = 0ul")
        self.execute("_idlbridge_pointer_count_ += 1")
        temp_id = self.get("_idlbridge_pointer_count_")
        temp_name = "_idlbridge_pointer_{id}_".format(id=temp_id)

        # Copy (anonymous) pointer variable to a known variable.
        # There is no way to get the variable name for pointers embedded in structures so we need to
        # copy the vptr to a new variable. We need a variable name we can access for de-referencing.
        byte_string = temp_name.encode("UTF8")
        temp_vptr = IDL_FindNamedVariable(byte_string, True)
        if temp_vptr == NULL:
            self.execute("_idlbridge_pointer_count_ -= 1")
            raise IDLLibraryError("Could not allocate IDL variable.")

        IDL_VarCopy(vptr, temp_vptr)

        # check pointer is not NULL, if so then clean up
        if self._is_null_pointer(temp_name):
            self.delete("{}".format(temp_name))
            self.execute("_idlbridge_pointer_count_ -= 1")
            return None

        # dereference the pointer using temporary to move the content
        self.execute("{}content_ = temporary(*{})".format(temp_name, temp_name))

        # get data from de-referenced variable
        data = self.get("{}content_".format(temp_name))

        # restore the pointer content, this unsets the content variable
        self.execute("*{} = temporary({}content_)".format(temp_name, temp_name))

        # clean up
        self.delete("{}".format(temp_name))
        self.delete("{}content_".format(temp_name))
        self.execute("_idlbridge_pointer_count_ -= 1")

        return data

    cdef inline bint _is_null_pointer(self, str variable):

        self.execute("_idlbridge_is_null_ = 0 & if {} eq ptr_new() then _idlbridge_is_null_ = 1".format(variable))
        if self.get("_idlbridge_is_null_") == 1:
            return True
        return False

    cpdef object put(self, str variable, object data):
        """
        Sets an IDL variable with python data.

        :param variable: A string containing the variable name.
        :param data: A Python object containing data to send.
        """

        cdef IDL_VPTR temp_vptr, dest_vptr

        # add support for lists by converting them to ndarrays
        if isinstance(data, list):
            data = np.array(data)

        # call the appropriate type handler
        if isinstance(data, dict):
            self._put_structure(variable, data)
            return

        elif isinstance(data, np.ndarray):
            temp_vptr = self._put_array(variable, data)
        else:
            temp_vptr = self._put_scalar(variable, data)

        # create/locate IDL variable
        byte_string = variable.encode("UTF8")
        dest_vptr = IDL_FindNamedVariable(byte_string, True)
        if dest_vptr == NULL:
            raise IDLLibraryError("Could not allocate IDL variable.")

        # populate variable with new data
        IDL_VarCopy(temp_vptr, dest_vptr)

    cdef inline object _put_structure(self, str name, dict data):
        """
        Create a structure in IDL from dictionary in Python.

        This method isn't the most efficient way to send structure data.
        Unfortunately the IDL C structure API is a completely brain dead design
        and offers no opportunity for code reuse, you basically have to
        implement every type again just for structures. The small speed
        decrease is worth the trade off for maintainable (bug free) code.
        """

        self.put("_idlbridge_depth_", 0)

        # build structure in temporary variable
        tempvar = "_idlbridge_tmp_"
        self._build_idl_structure(tempvar, data)

        # assign complete structure to target variable
        self.execute("{name} = {tempvar}".format(name=name, tempvar=tempvar))

    cdef inline object _build_idl_structure(self, str name, dict data):

        # Unlike python dictionary keys, IDL structure tags are case-insensitive.
        # Converting the keys to tags could result in duplicate names, this must be prevented.
        if not self._tags_unique(data):
            raise IDLValueError("Duplicate tag (key) name found. IDL structure tags are case insensitive and must be unique.")

        # create blank structure
        self.execute("{name} = {{}}".format(name=name))
        tempvar = "_idlbridge_v{depth}_".format(depth=self.get("_idlbridge_depth_"))
        for key, item in data.items():

            if isinstance(item, dict):

                # IDL can not handle empty structures as leaves in a tree
                if not item:
                    raise IDLValueError("IDL cannot handle empty structures nested inside another structure.")

                self.execute("_idlbridge_depth_ = _idlbridge_depth_ + 1")
                self._build_idl_structure(tempvar, item)
                self.execute("_idlbridge_depth_ = _idlbridge_depth_ - 1")

            else:

                self.put(tempvar, item)

            # append item to structure
            self.execute("{name} = create_struct(\"{key}\", {tempvar}, {name})".format(name=name, key=key, tempvar=tempvar))

    cdef inline bint _tags_unique(self, dict data) except *:

        cdef:
            list keys
            int index

        if len(data) < 2:
            return True

        # extract keys as a list, make lower case and sort
        keys = [key.lower() for key in data.keys()]
        keys.sort()

        # if keys are duplicated, they will be adjacent due to the sort
        # step through comparing adjacent keys
        for index in range(len(keys) - 1):
            if keys[index] == keys[index + 1]:
                return False
        return True

    cdef inline IDL_VPTR _put_array(self, str variable, np.ndarray data) except *:

        cdef:
            int type, num_dimensions, index
            IDL_ARRAY_DIM dimensions
            IDL_VPTR temp_vptr
            IDL_STRING string
            void *array_data

        if np.PyArray_SIZE(data) == 0:
            raise IDLValueError("IDL cannot handle empty arrays.")

        # convert dimensions to IDL
        num_dimensions = np.PyArray_NDIM(data)
        if num_dimensions > IDL_MAX_ARRAY_DIM:
            raise IDLValueError("Array contains more dimensions than IDL can handle (array has {} dimensions, IDL maximum is {}).".format(num_dimensions, IDL_MAX_ARRAY_DIM))

        self._dimensions_numpy_to_idl(dimensions, num_dimensions, np.PyArray_DIMS(data))

        # create temporary array and copy data
        temp_vptr = IDL_Gettmp()
        if temp_vptr == NULL:
            raise IDLLibraryError("Could not allocate IDL variable.")

        # string type requires special handling
        if np.PyArray_ISSTRING(data):

            array_data = <void *> IDL_MakeTempArray(IDL_TYP_STRING, num_dimensions, dimensions, IDL_ARR_INI_NOP, &temp_vptr)

            # flatten array
            data = np.PyArray_Ravel(data, np.NPY_ANYORDER)

            # convert strings to IDL_Strings
            for index in range(np.PyArray_SIZE(data)):
                byte_string = data[index].encode("UTF8")
                IDL_StrStore(&(<IDL_STRING *> array_data)[index], byte_string)

        else:

            # obtain IDL type
            type = self._type_numpy_to_idl(np.PyArray_TYPE(data))
            array_data = <void *> IDL_MakeTempArray(type, num_dimensions, dimensions, IDL_ARR_INI_NOP, &temp_vptr)
            memcpy(array_data, np.PyArray_DATA(data), np.PyArray_NBYTES(data))

        return temp_vptr

    cdef inline IDL_VPTR _put_scalar(self, str variable, object data) except *:

        cdef IDL_VPTR temp_vptr

        # create appropriate IDL temporary variable
        if isinstance(data, int):

            # select an int of the appropriate size (min int16)
            if -32768 <= data <= 32767:
                temp_vptr = IDL_GettmpInt(<IDL_INT> data)
            elif -2147483648 <= data <= 2147483647:
                temp_vptr = IDL_GettmpLong(<IDL_LONG> data)
            else:
                temp_vptr = IDL_GettmpLong64(<IDL_LONG64> data)

        elif isinstance(data, np.int16):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_INT
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.i)

        elif isinstance(data, np.int32):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_LONG
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.l)

        elif isinstance(data, np.int64):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_LONG64
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.l64)

        elif isinstance(data, np.uint8):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_BYTE
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.c)

        elif isinstance(data, np.uint16):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_UINT
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.ui)

        elif isinstance(data, np.uint32):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_ULONG
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.ul)

        elif isinstance(data, np.uint64):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_ULONG64
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.ul64)

        elif isinstance(data, float):

            temp_vptr = IDL_GettmpFloat(<double> data)

        elif isinstance(data, np.float32):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_FLOAT
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.f)

        elif isinstance(data, np.float64):

            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_DOUBLE
                np.PyArray_ScalarAsCtype(data, <void *> &temp_vptr.value.d)

        elif isinstance(data, (complex, np.complex64)):

            # there is no get complex temporary function
            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_COMPLEX
                temp_vptr.value.cmp.r = data.real
                temp_vptr.value.cmp.i = data.imag

        elif isinstance(data, (complex, np.complex128)):

            # there is no get complex temporary function
            temp_vptr = IDL_Gettmp()
            if temp_vptr != NULL:
                temp_vptr.type = IDL_TYP_DCOMPLEX
                temp_vptr.value.dcmp.r = data.real
                temp_vptr.value.dcmp.i = data.imag

        elif isinstance(data, str):

            byte_string = data.encode("UTF8")
            temp_vptr = IDL_StrToSTRING(byte_string)

        else:

            raise TypeError("Unsupported Python type. The following python and numpy types are supported: "
                            + "int, float, complex, str, list, dict, "
                            + "int16, int32, int64, uint8, uint16, uint32,"
                            + " uint64, float32, float64, complex64, complex128, ndarray.")

        if temp_vptr == NULL:
            raise IDLLibraryError("Could not allocate IDL variable.")

        return temp_vptr

    cpdef object delete(self, str variable):
        """
        Deletes the specified IDL variable.

        :param variable: A string specifying the name of the IDL variable to delete.
        :return: None
        """

        self.execute("delvar, {}".format(variable))

    cpdef object export_function(self, str name, list return_arguments=None):
        """
        Wraps an IDL function in an object that behaves like a Python function.

        For example, to gain access to the IDL "sin" function type:

            sin = idl.export_function("sin")

        Use "sin" like an ordinary python function:

            v = sin(0.5)

        Keyword arguments are specified using the normal Python syntax. To provide
        an IDL "/keyword", simply set the keyword equal to True in python.

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

        return IDLFunction(name, return_arguments, idl_bridge=self)

    cpdef object export_procedure(self, str name, list return_arguments=None):
        """
        Wraps an IDL procedure in an object that behaves like a Python function.

        For example, to gain access to the IDL "plot" procedure type:

            plot = idl.export_procedure("plot")

        Use "plot" like an ordinary python function:

            plot([1,2,3], [4,5,6])

        Keyword arguments are specified using the normal Python syntax. To provide
        an IDL "/keyword", simply set the keyword equal to True in python.

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

        :param name: A string specifying the name of the IDL procedure to wrap.
        :param return_arguments: A list object containing the index of
        arguments to return.
        :return: An IDLProcedure object.
        """

        return IDLProcedure(name, return_arguments, idl_bridge=self)

    cdef inline str _string_idl_to_py(self, IDL_STRING string):
        """
        Converts an IDL string object to a python string.

        :param string: An IDL string structure.
        :return: A python string object.
        """

        # The string pointer in the IDL string structure is invalid when the string length is zero.
        if string.slen == 0:
            return ""
        else:
            return string.s.decode("UTF8")

    cdef inline int _type_idl_to_numpy(self, int type) except *:
        """
        Maps IDL type values to numpy type values.

        :param type: An IDL type value.
        :return: A numpy type value.
        """

        if type == IDL_TYP_INT: return np.NPY_INT16
        elif type == IDL_TYP_LONG: return np.NPY_INT32
        elif type == IDL_TYP_LONG64: return np.NPY_INT64
        elif type == IDL_TYP_BYTE: return np.NPY_UINT8
        elif type == IDL_TYP_UINT: return np.NPY_UINT16
        elif type == IDL_TYP_ULONG: return np.NPY_UINT32
        elif type == IDL_TYP_ULONG64: return np.NPY_UINT64
        elif type == IDL_TYP_FLOAT: return np.NPY_FLOAT32
        elif type == IDL_TYP_DOUBLE: return np.NPY_FLOAT64
        elif type == IDL_TYP_COMPLEX: return np.NPY_COMPLEX64
        elif type == IDL_TYP_DCOMPLEX: return np.NPY_COMPLEX128
        elif type == IDL_TYP_STRING: return np.NPY_STRING
        else:
            raise IDLTypeError("No matching numpy data type defined for given IDL type.")

    cdef inline int _type_numpy_to_idl(self, int type) except *:
        """
        Maps numpy type values to IDL type values.

        :param type: A numpy type value.
        :return: An IDL type value.
        """

        if type == np.NPY_INT8:
            raise IDLTypeError("IDL does not support signed bytes.")
        elif type == np.NPY_INT16: return IDL_TYP_INT
        elif type == np.NPY_INT32: return IDL_TYP_LONG
        elif type == np.NPY_INT64: return IDL_TYP_LONG64
        elif type == np.NPY_UINT8: return IDL_TYP_BYTE
        elif type == np.NPY_UINT16: return IDL_TYP_UINT
        elif type == np.NPY_UINT32: return IDL_TYP_ULONG
        elif type == np.NPY_UINT64: return IDL_TYP_ULONG64
        elif type == np.NPY_FLOAT32: return IDL_TYP_FLOAT
        elif type == np.NPY_FLOAT64: return IDL_TYP_DOUBLE
        elif type == np.NPY_COMPLEX64: return IDL_TYP_COMPLEX
        elif type == np.NPY_COMPLEX128: return IDL_TYP_DCOMPLEX
        elif type == np.NPY_STRING: return IDL_TYP_STRING
        else:
            raise IDLTypeError("No matching IDL data type defined for given numpy type.")

    cdef inline void _dimensions_idl_to_numpy(self, np.npy_intp *numpy_dimensions, int dimension_count, IDL_ARRAY_DIM idl_dimensions):
        """
        Converts an IDL dimension array to a numpy dimension array.

        IDL defines dimensions in the opposite order to numpy.
        This method inverts the dimension order.
        """

        cdef int index

        # IDL defines its dimensions with the opposite order to numpy, invert the order
        for index in range(dimension_count):
            numpy_dimensions[index] = idl_dimensions[dimension_count - (index + 1)]

    cdef inline void _dimensions_numpy_to_idl(self, IDL_MEMINT *idl_dimensions, int dimension_count, np.npy_intp *numpy_dimensions):
        """
        Converts a numpy dimension array to an IDL dimension array.

        IDL defines dimensions in the opposite order to numpy.
        This method inverts the dimension order.
        """

        cdef int index

        # IDL defines its dimensions with the opposite order to numpy, invert the order
        for index in range(dimension_count):
            idl_dimensions[index] = numpy_dimensions[dimension_count - (index + 1)]


class _IDLCallable:

    def __init__(self, name, return_arguments=None, idl_bridge=IDLBridge()):

        self.name = name
        self._idl = idl_bridge
        self._return_arguments = return_arguments

    def _process_arguments(self, arguments, temporary_variables):

        # parse arguments
        argument_variables = []
        for index, argument in enumerate(arguments):

            # transfer argument to idl
            tempvar = "_idlbridge_arg{index}".format(index=index)
            self._idl.put(tempvar, argument)

            # record temporary variable for later cleanup
            argument_variables.append(tempvar)

        # add argument temporaries to list of temporary variables
        temporary_variables += argument_variables

        # build and return argument command string fragment
        return ", ".join(argument_variables)

    def _process_keywords(self, keywords, temporary_variables):

        keyword_strings = []
        for index, (key, argument) in enumerate(keywords.items()):

            # transfer argument
            tempvar = "idlbridge_kw{index}".format(index=index)
            self._idl.put(tempvar, argument)

            # generate key string for command
            keyword_strings.append("{key}={var}".format(key=key, var=tempvar))

            # record variable for later cleanup
            temporary_variables.append(tempvar)

        # build and return keyword command string fragment
        return ", ".join(keyword_strings)

    def _process_return_arguments(self, arguments):

        return_arguments = []

        if self._return_arguments:
            max_args = len(arguments)
            for index in self._return_arguments:
                # only return arguments that were passed in by the user to the function
                if index < max_args:
                    return_arguments.append(self._idl.get("_idlbridge_arg{index}".format(index=index)))

        return return_arguments


class IDLFunction(_IDLCallable):

    def __call__(self, *arguments, **keywords):

        temporary_variables = []

        # pass arguments to idl and assemble the relevant command string fragments
        argument_fragment = self._process_arguments(arguments, temporary_variables)
        keyword_fragment = self._process_keywords(keywords, temporary_variables)

        # assemble command string
        return_variable = "_idlbridge_return"
        command = "{rtnvar} = {name}({arg}".format(rtnvar=return_variable, name=self.name, arg=argument_fragment)

        # need an extra comma to separate arguments from keywords if both present
        if argument_fragment and keyword_fragment:
            command += ", "

        command += "{key})".format(key=keyword_fragment)

        # execute command and obtain returned data
        self._idl.execute(command)
        return_value = self._idl.get(return_variable)

        # if modified arguments need to be returned, obtain and pack into a tuple with the return value
        return_arguments = self._process_return_arguments(arguments)
        if return_arguments:
            return_value = tuple([return_value] + return_arguments)

        # clean up
        for variable in temporary_variables:
            self._idl.delete(variable)
        self._idl.delete(return_variable)

        return return_value


class IDLProcedure(_IDLCallable):

    def __call__(self, *arguments, **keywords):

        temporary_variables = []

        # pass arguments to idl and assemble the relevant command string fragments
        argument_fragment = self._process_arguments(arguments, temporary_variables)
        keyword_fragment = self._process_keywords(keywords, temporary_variables)

        # assemble command string
        if argument_fragment or keyword_fragment:

            command = "{name}, {arg}".format(name=self.name, arg=argument_fragment)

            # need an extra comma to separate arguments from keywords if present
            if argument_fragment and keyword_fragment:
                command += ", "

            command += keyword_fragment

        else:

            command = self.name

        # execute command
        self._idl.execute(command)

        # if modified arguments need to be returned, obtain and pack into a tuple
        return_arguments = self._process_return_arguments(arguments)
        if return_arguments:
            return_value = tuple(return_arguments)
        else:
            return_value = None

        # clean up
        for variable in temporary_variables:
            self._idl.delete(variable)

        return return_value

