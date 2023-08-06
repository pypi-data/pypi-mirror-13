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
Cython wrapper for required parts of idl_export.h (IDL v8.x)
"""

cdef extern from "idl_export.h":

    # data types
    ctypedef unsigned char UCHAR

    IF UNAME_MACHINE == "i686" or UNAME_MACHINE == "x86":

        # 32bit systems (x86)

        # IDL data types
        ctypedef short IDL_INT
        ctypedef unsigned short IDL_UINT
        ctypedef long IDL_LONG
        ctypedef unsigned long IDL_ULONG
        ctypedef long long IDL_LONG64
        ctypedef unsigned long long IDL_ULONG64

        # IDL index types
        ctypedef IDL_LONG IDL_MEMINT
        ctypedef IDL_ULONG IDL_UMEMINT

    ELSE:

        # 64bit systems (x86_64)

        # IDL data types
        ctypedef short IDL_INT
        ctypedef unsigned short IDL_UINT
        ctypedef int IDL_LONG
        ctypedef unsigned int IDL_ULONG
        ctypedef long long IDL_LONG64
        ctypedef unsigned long long IDL_ULONG64

        # IDL index types
        ctypedef IDL_LONG64 IDL_MEMINT
        ctypedef IDL_ULONG64 IDL_UMEMINT

    # IDL_VARIABLE type values
    DEF IDL_TYP_UNDEF = 0
    DEF IDL_TYP_BYTE = 1
    DEF IDL_TYP_INT = 2
    DEF IDL_TYP_LONG = 3
    DEF IDL_TYP_FLOAT = 4
    DEF IDL_TYP_DOUBLE = 5
    DEF IDL_TYP_COMPLEX = 6
    DEF IDL_TYP_STRING = 7
    DEF IDL_TYP_STRUCT = 8
    DEF IDL_TYP_DCOMPLEX = 9
    DEF IDL_TYP_PTR = 10
    DEF IDL_TYP_OBJREF = 11
    DEF IDL_TYP_UINT = 12
    DEF IDL_TYP_ULONG = 13
    DEF IDL_TYP_LONG64 = 14
    DEF IDL_TYP_ULONG64 = 15

    # IDL_VARIABLE flags
    DEF IDL_V_CONST = 1
    DEF IDL_V_CONST = 2
    DEF IDL_V_ARR = 4
    DEF IDL_V_FILE = 8
    DEF IDL_V_DYNAMIC = 16
    DEF IDL_V_STRUCT = 32
    DEF IDL_V_NOT_SCALAR = (IDL_V_ARR | IDL_V_FILE | IDL_V_STRUCT)

    # array init constants
    DEF IDL_ARR_INI_ZERO = 0	    # Zero data area
    DEF IDL_ARR_INI_NOP = 1         # Don't do anything to data area
    DEF IDL_ARR_INI_INDEX = 2	    # Put 1-D index into each elt.
    DEF IDL_ARR_INI_TEST = 3        # Test if enough memory is available

    # init defines
    DEF IDL_INIT_BACKGROUND	= 32
    DEF IDL_INIT_QUIET = 64
    DEF IDL_INIT_NOCMDLINE = (1 << 12)

    # initialisation data structures
    ctypedef int IDL_INIT_DATA_OPTIONS_T

    ctypedef struct IDL_CLARGS:

        int argc
        char **argv

    ctypedef struct IDL_INIT_DATA:

        IDL_INIT_DATA_OPTIONS_T options
        IDL_CLARGS clargs
        void *hwnd

    # complex type structures
    ctypedef struct IDL_COMPLEX:

        float r, i

    ctypedef struct IDL_DCOMPLEX:

        double r, i

    # array structures
    DEF IDL_MAX_ARRAY_DIM = 8

    ctypedef IDL_MEMINT IDL_ARRAY_DIM[IDL_MAX_ARRAY_DIM]

    ctypedef struct IDL_ARRAY:

        IDL_MEMINT elt_len          # Length of element in char units
        IDL_MEMINT arr_len          # Length of entire array (char)
        IDL_MEMINT n_elts           # total # of elements
        UCHAR *data                 # ^ to beginning of array data
        UCHAR n_dim                 # # of dimensions used by array
        UCHAR flags                 # Array block flags
        short file_unit             # # of assoc file if file var
        IDL_ARRAY_DIM dim           # dimensions
        # IDL_ARRAY_FREE_CB free_cb 	# Free callback
        # IDL_FILEINT offset		    # Offset to base of data for file var
        # IDL_MEMINT data_guard 	    # Guard longword

    # structure type
    ctypedef struct _idl_structure:

        int ntags

    ctypedef _idl_structure *IDL_StructDefPtr

    ctypedef struct IDL_SREF:

        IDL_ARRAY *arr              # pointer to array block containing data
        _idl_structure *sdef        # pointer to structure definition

    DEF IDL_STD_INHERIT = 1

    ctypedef struct IDL_STRUCT_TAG_DEF:

        char *name
        IDL_MEMINT *dims
        void *type
        UCHAR flags

    # string type
    ctypedef int IDL_STRING_SLEN_T

    DEF IDL_STRING_MAX_SLEN = 2147483647

    ctypedef struct IDL_STRING:

        IDL_STRING_SLEN_T slen
        short stype
        char *s

    # variable structures
    ctypedef union IDL_ALLTYPES:

        UCHAR c
        IDL_INT i
        IDL_UINT ui
        IDL_LONG l
        IDL_ULONG ul
        IDL_LONG64 l64
        IDL_ULONG64 ul64
        float f
        double d
        IDL_COMPLEX cmp
        IDL_DCOMPLEX dcmp
        IDL_STRING str
        IDL_ARRAY *arr
        IDL_SREF s
        #IDL_HVID hvid
        IDL_MEMINT memint
        #IDL_FILEINT fileint
        #IDL_PTRINT ptrint

    # IDL_VARIABLE definition
    ctypedef struct IDL_VARIABLE:

        UCHAR type
        UCHAR flags
        UCHAR flags2
        IDL_ALLTYPES value

    ctypedef IDL_VARIABLE *IDL_VPTR

    # IDL message flags
    DEF IDL_M_GENERIC = -1
    DEF IDL_M_NAMED_GENERIC = -2
    DEF IDL_M_SYSERR = -4
    DEF IDL_M_BADARRDIM = -174

    # functions
    int IDL_Initialize(IDL_INIT_DATA *init_data) nogil

    int IDL_Cleanup(int just_cleanup) nogil

    int IDL_ExecuteStr(char *cmd) nogil

    IDL_VPTR IDL_FindNamedVariable(char *name, int ienter) nogil

    void IDL_Delvar(IDL_VPTR var) nogil

    IDL_VPTR IDL_Gettmp() nogil

    IDL_VPTR IDL_GettmpByte(UCHAR value) nogil

    IDL_VPTR IDL_GettmpInt(IDL_INT value) nogil

    IDL_VPTR IDL_GettmpUInt(IDL_UINT value) nogil

    IDL_VPTR IDL_GettmpLong(IDL_LONG value) nogil

    IDL_VPTR IDL_GettmpULong(IDL_ULONG value) nogil

    IDL_VPTR IDL_GettmpLong64(IDL_LONG64 value) nogil

    IDL_VPTR IDL_GettmpULong64(IDL_ULONG64 value) nogil

    IDL_VPTR IDL_GettmpFloat(float value) nogil

    IDL_VPTR IDL_GettmpDouble(double value) nogil

    char *IDL_MakeTempArray(int type, int n_dim, IDL_MEMINT dim[], int init, IDL_VPTR *var) nogil

    void IDL_Deltmp(IDL_VPTR p)

    void IDL_VarCopy(IDL_VPTR src, IDL_VPTR dst) nogil

    char *IDL_VarGetString(IDL_VPTR vptr) nogil

    IDL_VPTR IDL_StrToSTRING(char *s) nogil

    void IDL_StrStore(IDL_STRING *s, const char *fs) nogil

    int IDL_StructNumTags(IDL_StructDefPtr sdef) nogil

    char *IDL_StructTagNameByIndex(IDL_StructDefPtr sdef, int index, int msg_action, char **struct_name) nogil

    IDL_MEMINT IDL_StructTagInfoByIndex(IDL_StructDefPtr sdef, int index,int msg_action, IDL_VPTR *var) nogil

    char *IDL_MakeTempStruct(IDL_StructDefPtr sdef, int n_dim, IDL_MEMINT *dim, IDL_VPTR *var, int zero) nogil

    IDL_StructDefPtr IDL_MakeStruct(char *name, IDL_STRUCT_TAG_DEF *tags) nogil

    char *IDL_VarName(IDL_VPTR v) nogil