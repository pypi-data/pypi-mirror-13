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

from unittest import TestCase
from os.path import join, dirname, abspath
import numpy as np
import idlbridge as idl

# extend idl path to allow access to test functions
test_function_path = join(dirname(abspath(__file__)), "idl_routines.pro")
idl.execute(".compile {}".format(test_function_path))

class TestIDLBridge(TestCase):

    def assertArrayEqual(self, first, second, message):

        # check data types are the same
        self.assertEqual(first.dtype, second.dtype, message + " Data types are different.")

        # check all elements are equal
        self.assertTrue((first == second).any(), message + " Elements are not the same.")

    def test_execute(self):

        # This function is difficult to test as it requires the other functions.
        # Here we just test the command executes without a failure.
        # Basically if this fails evey test is going to fail!
        idl.execute("d = 128")

    def test_get_missing(self):

        # create and delete variable in idl to ensure it does not exist!
        idl.execute("test_get_missing = 1")
        idl.execute("delvar, test_get_missing")

        with self.assertRaises(idl._core.IDLValueError):

            idl.get("test_get_missing")

    def test_get_scalar_byte(self):

        # unsigned byte
        idl.execute("test_get_byte = byte(15)")
        self.assertEqual(15, idl.get("test_get_byte"), "Failed to get unsigned byte.")

    def test_get_scalar_int(self):

        # signed integer
        idl.execute("test_get_int = fix(-3485)")
        self.assertEqual(-3485, idl.get("test_get_int"), "Failed to get signed integer.")

    def test_get_scalar_uint(self):

        # unsigned integer
        idl.execute("test_get_uint = uint(36640)")
        self.assertEqual(36640, idl.get("test_get_uint"), "Failed to get unsigned integer.")

    def test_get_scalar_long(self):

        # signed long
        idl.execute("test_get_long = long(-1633485)")
        self.assertEqual(-1633485, idl.get("test_get_long"), "Failed to get signed long.")

    def test_get_scalar_ulong(self):

        # unsigned long
        idl.execute("test_get_ulong = ulong(3267987588)")
        self.assertEqual(3267987588, idl.get("test_get_ulong"), "Failed to get unsigned long.")

    def test_get_scalar_long64(self):

        # signed long64
        idl.execute("test_get_long64 = long64(-16000000096790)")
        self.assertEqual(-16000000096790, idl.get("test_get_long64"), "Failed to get signed long64.")

    def test_get_scalar_ulong64(self):

        # unsigned long64
        idl.execute("test_get_ulong64 = ulong64(18446728073709454827)")
        self.assertEqual(18446728073709454827, idl.get("test_get_ulong64"), "Failed to get unsigned long64.")

    def test_get_scalar_float(self):

        # float
        idl.execute("test_get_float = float(-2.0)")
        self.assertEqual(-2.0, idl.get("test_get_float"), "Failed to get float.")

    def test_get_scalar_double(self):

        # double
        idl.execute("test_get_double = double(1.0)")
        self.assertEqual(1.0, idl.get("test_get_double"), "Failed to get double.")

    def test_get_scalar_complex_float(self):

        # float complex
        idl.execute("test_get_fcomplex = complex(1.0, 2.0)")
        self.assertEqual(complex(1.0, 2.0), idl.get("test_get_fcomplex"), "Failed to get float complex.")

    def test_get_scalar_complex_double(self):

        # double complex
        idl.execute("test_get_dcomplex = dcomplex(1.0, 2.0)")
        self.assertEqual(complex(1.0, 2.0), idl.get("test_get_dcomplex"), "Failed to get double complex.")

    def test_get_array_byte(self):

        # 1D array, byte
        idl.execute("test_get_array_1d_byte = byte([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_byte")
        r = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
        self.assertArrayEqual(v, r, "Failed to get byte array.")

    def test_get_array_int(self):

        # 1D array, int
        idl.execute("test_get_array_1d_int = fix([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_int")
        r = np.array([1, 2, 3, 4, 5], dtype=np.int16)
        self.assertArrayEqual(v, r, "Failed to get int array.")

    def test_get_array_uint(self):

        # 1D array, uint
        idl.execute("test_get_array_1d_uint = uint([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_uint")
        r = np.array([1, 2, 3, 4, 5], dtype=np.uint16)
        self.assertArrayEqual(v, r, "Failed to get uint array.")

    def test_get_array_long(self):

        # 1D array, long
        idl.execute("test_get_array_1d_long = long([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_long")
        r = np.array([1, 2, 3, 4, 5], dtype=np.int32)
        self.assertArrayEqual(v, r, "Failed to get long array.")

    def test_get_array_ulong(self):

        # 1D array, ulong
        idl.execute("test_get_array_1d_ulong = ulong([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_ulong")
        r = np.array([1, 2, 3, 4, 5], dtype=np.uint32)
        self.assertArrayEqual(v, r, "Failed to get ulong array.")

    def test_get_array_long64(self):

        # 1D array, long64
        idl.execute("test_get_array_1d_long64 = long64([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_long64")
        r = np.array([1, 2, 3, 4, 5], dtype=np.int64)
        self.assertArrayEqual(v, r, "Failed to get long64 array.")

    def test_get_array_ulong64(self):

        # 1D array, ulong64
        idl.execute("test_get_array_1d_ulong64 = ulong64([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_ulong64")
        r = np.array([1, 2, 3, 4, 5], dtype=np.uint64)
        self.assertArrayEqual(v, r, "Failed to get ulong64 array.")

    def test_get_array_float(self):

        # 1D array, float
        idl.execute("test_get_array_1d_float = float([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_float")
        r = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        self.assertArrayEqual(v, r, "Failed to get float array.")

    def test_get_array_double(self):

        # 1D array, double
        idl.execute("test_get_array_1d_double = double([1,2,3,4,5])")
        v = idl.get("test_get_array_1d_double")
        r = np.array([1, 2, 3, 4, 5], dtype=np.float64)
        self.assertArrayEqual(v, r, "Failed to get double array.")

    def test_get_array_complex_float(self):

        # 1D array, complex float
        idl.execute("test_get_array_1d_complex = complex([1,2,3,4,5], [6,7,8,9,10])")
        v = idl.get("test_get_array_1d_complex")
        r = np.array([1+6j, 2+7j, 3+8j, 4+9j, 5+10j], dtype=np.complex64)
        self.assertArrayEqual(v, r, "Failed to get complex float array.")

    def test_get_array_complex_double(self):

        # 1D array, complex double
        idl.execute("test_get_array_1d_dcomplex = dcomplex([1,2,3,4,5], [6,7,8,9,10])")
        v = idl.get("test_get_array_1d_dcomplex")
        r = np.array([1+6j, 2+7j, 3+8j, 4+9j, 5+10j], dtype=np.complex128)
        self.assertArrayEqual(v, r, "Failed to get complex double array.")

    def test_get_array_string(self):

        # 1D array, string
        idl.execute("test_get_array_1d_string = [\"dog\", \"\", \"cat\", \"fish\"]")
        v = idl.get("test_get_array_1d_string")
        r = np.array(["dog", "", "cat", "fish"])
        self.assertArrayEqual(v, r, "Failed to get string array.")

    def test_get_array_multidimensional(self):

        # ND array
        idl.execute("test_get_array_nd = indgen(8,7,6,5,4,3,2,1,/long)")
        v = np.arange(8*7*6*5*4*3*2*1, dtype=np.int32).reshape((1, 2, 3, 4, 5, 6, 7, 8))
        r = idl.get("test_get_array_nd")
        self.assertArrayEqual(v, r, "Failed to get multidimensional array.")

    def test_get_structure_basic(self):

        idl.execute("test_get_structure_basic = {a:byte(1), b:fix(2), "
                    + "c:uint(3), d:long(4), e:ulong(5), f:long64(6), "
                    + "g:ulong64(7), h:float(1.0), i:double(2.0), "
                    + "j:complex(1.0, 2.0), k:dcomplex(1.0, 2.0),"
                    + "l:\"test\"}")

        r = idl.get("test_get_structure_basic")

        v = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6,
             "g": 7, "h": 1.0, "i": 2.0, "j": 1+2j, "k": 1+2j,
             "l": "test"}

        self.assertEqual(v, r, "Failed to get basic structure.")

    def test_get_structure_array(self):

        idl.execute("test_get_structure_array = {a:[1, 2, 3, 4, 5], s:{a:1, b:2, c:7}}")
        r = idl.get("test_get_structure_array")

        v = {"a": np.array([1, 2, 3, 4, 5], dtype=np.int16)}

        self.assertArrayEqual(v["a"], r["a"], "Failed to get array in structure.")

    def test_get_structure_nested(self):

        idl.execute("test_get_structure_nested = {a:{g:8, h:{s:\"hello\"}}, s:{a:1, b:2, c:7}}")
        r = idl.get("test_get_structure_nested")

        v = {"a": {"g": 8, "h": {"s": "hello"}}, "s": {"a": 1, "b": 2, "c": 7}}

        self.assertEqual(v, r, "Failed to get nested structure.")

    def test_get_string(self):

        # null string
        idl.execute("test_get_string_null = \"\"")
        self.assertEqual("", idl.get("test_get_string_null"), "Failed to get null string.")

        # normal string
        idl.execute("test_get_string_normal = \"this is a test string\"")
        self.assertEqual("this is a test string", idl.get("test_get_string_normal"), "Failed to get normal string.")

    def test_get_pointer_simple(self):

        idl.execute("test_get_pointer_simple = ptr_new(1234)")
        r = idl.get("test_get_pointer_simple")

        v = 1234

        self.assertEqual(v, r, "Failed to dereference pointer.")

    def test_get_pointer_chain(self):

        # 3 chained pointers
        idl.execute("test_get_pointer_chain = ptr_new(ptr_new(ptr_new(5678)))")
        r = idl.get("test_get_pointer_chain")

        v = 5678

        self.assertEqual(v, r, "Failed to dereference chained pointers.")

    def test_get_pointer_structure(self):

        idl.execute("test_get_pointer_structure = {p: ptr_new(159)}")
        r = idl.get("test_get_pointer_structure")

        v = {"p": 159}

        self.assertEqual(v, r, "Failed to dereference pointer nested into structure.")

    def test_get_pointer_null(self):

        idl.execute("test_get_pointer_null = ptr_new()")
        r = idl.get("test_get_pointer_null")

        v = None

        self.assertEqual(v, r, "Failed to dereference null pointer.")

    def test_put_scalar_int(self):

        idl.put("test_put_int", -574)
        self.assertEqual(-574, idl.get("test_put_int"), "Failed to put int.")

    def test_put_scalar_float(self):

        idl.put("test_put_float", 2.0)
        self.assertEqual(2.0, idl.get("test_put_float"), "Failed to put float.")

    def test_put_scalar_complex(self):

        idl.put("test_put_complex", 2.0+1.0j)
        self.assertEqual(2.0+1.0j, idl.get("test_put_complex"), "Failed to put complex.")

    def test_put_scalar_numpy_int16(self):

        idl.put("test_put_numpy_int16", np.int16(-1574))
        self.assertEqual(-1574, idl.get("test_put_numpy_int16"), "Failed to put numpy int16.")

    def test_put_scalar_numpy_int32(self):

        idl.put("test_put_numpy_int32", np.int32(-1015574))
        self.assertEqual(-1015574, idl.get("test_put_numpy_int32"), "Failed to put numpy int32.")

    def test_put_scalar_numpy_int64(self):

        idl.put("test_put_numpy_int64", np.int64(-10156545740))
        self.assertEqual(-10156545740, idl.get("test_put_numpy_int64"), "Failed to put numpy int64.")

    def test_put_scalar_numpy_uint8(self):

        idl.put("test_put_numpy_uint8", np.uint8(145))
        self.assertEqual(145, idl.get("test_put_numpy_uint8"), "Failed to put numpy uint8.")

    def test_put_scalar_numpy_uint16(self):

        idl.put("test_put_numpy_uint16", np.uint16(1574))
        self.assertEqual(1574, idl.get("test_put_numpy_uint16"), "Failed to put numpy uint16.")

    def test_put_scalar_numpy_uint32(self):

        idl.put("test_put_numpy_uint32", np.uint32(1015574))
        self.assertEqual(1015574, idl.get("test_put_numpy_uint32"), "Failed to put numpy uint32.")

    def test_put_scalar_numpy_uint64(self):

        idl.put("test_put_numpy_uint64", np.int64(10156545740))
        self.assertEqual(10156545740, idl.get("test_put_numpy_uint64"), "Failed to put numpy uint64.")

    def test_put_scalar_numpy_float32(self):

        idl.put("test_put_numpy_float32", np.float32(1.0))
        self.assertEqual(1.0, idl.get("test_put_numpy_float32"), "Failed to put numpy float32.")

    def test_put_scalar_numpy_float64(self):

        idl.put("test_put_numpy_float64", np.float64(-1.0))
        self.assertEqual(-1.0, idl.get("test_put_numpy_float64"), "Failed to put numpy float64.")

    def test_put_scalar_numpy_complex64(self):

        idl.put("test_put_numpy_complex64", np.complex64(2.0+1.0j))
        self.assertEqual(2.0+1.0j, idl.get("test_put_numpy_complex64"), "Failed to put numpy complex64.")

    def test_put_scalar_numpy_complex128(self):

        idl.put("test_put_numpy_complex128", np.complex128(2.0-1.0j))
        self.assertEqual(2.0-1.0j, idl.get("test_put_numpy_complex128"), "Failed to put numpy complex128.")

    def test_put_string(self):

        idl.put("test_put_string", "test")
        self.assertEqual("test", idl.get("test_put_string"), "Failed to put string.")

    def test_put_list(self):

        # lists get converted to numpy arrays by put
        v = [1, 2, 3, 4, 5]
        idl.put("test_put_list", v)
        self.assertArrayEqual(np.array(v), idl.get("test_put_list"), "Failed to put list.")

    def test_put_array_uint8(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.uint8)
        idl.put("test_put_array_1d_uint8", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_uint8"), "Failed to put uint8 array.")

    def test_put_array_int16(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.int16)
        idl.put("test_put_array_1d_int16", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_int16"), "Failed to put int16 array.")

    def test_put_array_uint16(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.uint16)
        idl.put("test_put_array_1d_uint16", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_uint16"), "Failed to put uint16 array.")

    def test_put_array_int32(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.int32)
        idl.put("test_put_array_1d_int32", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_int32"), "Failed to put int32 array.")

    def test_put_array_uint32(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.uint32)
        idl.put("test_put_array_1d_uint32", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_uint32"), "Failed to put uint32 array.")

    def test_put_array_int64(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.int64)
        idl.put("test_put_array_1d_int64", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_int64"), "Failed to put int64 array.")

    def test_put_array_uint64(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.uint64)
        idl.put("test_put_array_1d_uint64", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_uint64"), "Failed to put uint64 array.")

    def test_put_array_float32(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        idl.put("test_put_array_1d_float32", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_float32"), "Failed to put float32 array.")

    def test_put_array_float64(self):

        v = np.array([1, 2, 3, 4, 5], dtype=np.float64)
        idl.put("test_put_array_1d_float64", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_float64"), "Failed to put float64 array.")

    def test_put_array_complex64(self):

        v = np.array([1+6j, 2+7j, 3+8j, 4+9j, 5+10j], dtype=np.complex64)
        idl.put("test_put_array_1d_complex64", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_complex64"), "Failed to put complex64 array.")

    def test_put_array_complex128(self):

        v = np.array([1+6j, 2+7j, 3+8j, 4+9j, 5+10j], dtype=np.complex128)
        idl.put("test_put_array_1d_complex128", v)
        self.assertArrayEqual(v, idl.get("test_put_array_1d_complex128"), "Failed to put complex128 array.")

    def test_put_array_string(self):

        v = np.array([["dog", "", "lemon"], ["cat", "fish", "siren"]])
        idl.put("test_put_array_string", v)
        self.assertArrayEqual(v, idl.get("test_put_array_string"), "Failed to put string array.")

    def test_put_array_multidimensional(self):

        # ND array
        v = np.arange(8*7*6*5*4*3*2*1, dtype=np.int32).reshape((1, 2, 3, 4, 5, 6, 7, 8))
        idl.put("test_put_array_multidimensional", v)
        self.assertArrayEqual(v, idl.get("test_put_array_multidimensional"), "Failed to put multidimensional array.")

    def test_put_array_empty(self):

        # IDL can not handle empty arras
        with self.assertRaises(idl._core.IDLValueError):

            idl.put("test_put_array_empty", [])

    def test_put_structure_basic(self):

        v = {"a": 1, "b": 1.0, "c": 1+2j, "d": "test"}

        idl.put("test_put_structure_basic", v)

        self.assertEqual(v, idl.get("test_put_structure_basic"), "Failed to put basic structure.")

    def test_put_structure_array(self):

        v = {"a": np.array([1, 2, 3, 4, 5], dtype=np.int16), "b": np.array(["alpha", "beta"])}

        idl.put("test_put_structure_array", v)

        self.assertArrayEqual(v["a"], idl.get("test_put_structure_array")["a"], "Failed to put array structure (scalar array).")
        self.assertArrayEqual(v["b"], idl.get("test_put_structure_array")["b"], "Failed to put array structure (string array).")

    def test_put_structure_nested(self):

        v = {"s": {"a": 5, "b": 7}}

        idl.put("test_put_structure_nested", v)

        self.assertEqual(v, idl.get("test_put_structure_nested"), "Failed to put nested structure.")

    def test_put_structure_bad_keys(self):

        v = {"alpha": 1, "beta": 2, "Alpha": 3}

        with self.assertRaises(idl._core.IDLValueError):

            idl.put("test_put_structure_bad_keys", v)

    def test_put_structure_nested_empty(self):

        v = {"s": {}}

        with self.assertRaises(idl._core.IDLValueError):

            idl.put("test_put_structure_nested_empty", v)

    def test_delete(self):

        idl.execute("test_delete = 5")
        idl.delete("test_delete")
        with self.assertRaises(idl._core.IDLValueError):

            idl.get("test_delete")

    def test_function_basic_call(self):

        idl_test_function = idl.export_function("idl_test_function")
        self.assertEqual(999, idl_test_function(1, 2, 3, 4), "Calling function with basic arguments failed.")
        self.assertEqual(100, idl_test_function(1, 2, 3, 4, key_a=True), "Calling function with keyword argument failed (1 of 2).")
        self.assertEqual(5000, idl_test_function(1, 2, 3, 4, key_b=True), "Calling function with keyword argument failed (2 of 2).")

    def test_function_partial_returned_arguments_no_keywords(self):

        idl_test_function = idl.export_function("idl_test_function", return_arguments=[0, 2])
        rtn, a, c = idl_test_function(1.5, 2.5, 3.5, 4.5)
        self.assertEqual(a, 2.5, "Argument a was not correctly returned.")
        self.assertEqual(c, 4.5, "Argument c was not correctly returned.")
        self.assertEqual(rtn, 999, "The return value is incorrect.")

    def test_function_partial_returned_arguments_with_keywords(self):

        idl_test_function = idl.export_function("idl_test_function", return_arguments=[0, 2])
        rtn, a, c = idl_test_function(1.5, 2.5, 3.5, 4.5, key_a=True)
        self.assertEqual(a, 20, "Argument a was not correctly returned.")
        self.assertEqual(c, 60, "Argument c was not correctly returned.")
        self.assertEqual(rtn, 100, "The return value is incorrect.")

    def test_function_full_returned_arguments_no_keywords(self):

        idl_test_function = idl.export_function("idl_test_function", return_arguments=[0, 1, 2, 3])
        rtn, a, b, c, d = idl_test_function(1.5, 2.5, 3.5, 4.5)
        self.assertEqual(a, 2.5, "Argument a was not correctly returned.")
        self.assertEqual(b, 3.5, "Argument b was not correctly returned.")
        self.assertEqual(c, 4.5, "Argument c was not correctly returned.")
        self.assertEqual(d, 0.0, "Argument d was not correctly returned.")
        self.assertEqual(rtn, 999, "The return value is incorrect.")

    def test_function_full_returned_arguments_with_keywords(self):

        idl_test_function = idl.export_function("idl_test_function", return_arguments=[0, 1, 2, 3])
        rtn, a, b, c, d = idl_test_function(1.5, 2.5, 3.5, 4.5, key_b=True)
        self.assertEqual(a, 1000, "Argument a was not correctly returned.")
        self.assertEqual(b, 2000, "Argument b was not correctly returned.")
        self.assertEqual(c, 3000, "Argument c was not correctly returned.")
        self.assertEqual(d, 4000, "Argument d was not correctly returned.")
        self.assertEqual(rtn, 5000, "The return value is incorrect.")

    def test_procedure_basic_call(self):

        idl_test_procedure = idl.export_procedure("idl_test_procedure")
        self.assertEqual(None, idl_test_procedure(1, 2, 3, 4), "Calling procedure with basic arguments failed.")
        self.assertEqual(None, idl_test_procedure(1, 2, 3, 4, key_a=True), "Calling procedure with keyword argument failed (1 of 2).")
        self.assertEqual(None, idl_test_procedure(1, 2, 3, 4, key_b=True), "Calling procedure with keyword argument failed (2 of 2).")

    def test_procedure_partial_returned_arguments_no_keywords(self):

        idl_test_procedure = idl.export_procedure("idl_test_procedure", return_arguments=[0, 2])
        a, c = idl_test_procedure(1.5, 2.5, 3.5, 4.5)
        self.assertEqual(a, 2.5, "Argument a was not correctly returned.")
        self.assertEqual(c, 4.5, "Argument c was not correctly returned.")

    def test_procedure_partial_returned_arguments_with_keywords(self):

        idl_test_procedure = idl.export_procedure("idl_test_procedure", return_arguments=[0, 2])
        a, c = idl_test_procedure(1.5, 2.5, 3.5, 4.5, key_a=True)
        self.assertEqual(a, 40, "Argument a was not correctly returned.")
        self.assertEqual(c, 80, "Argument c was not correctly returned.")

    def test_procedure_full_returned_arguments_no_keywords(self):

        idl_test_procedure = idl.export_procedure("idl_test_procedure", return_arguments=[0, 1, 2, 3])
        a, b, c, d = idl_test_procedure(1.5, 2.5, 3.5, 4.5)
        self.assertEqual(a, 2.5, "Argument a was not correctly returned.")
        self.assertEqual(b, 3.5, "Argument b was not correctly returned.")
        self.assertEqual(c, 4.5, "Argument c was not correctly returned.")
        self.assertEqual(d, 0.0, "Argument d was not correctly returned.")

    def test_procedure_full_returned_arguments_with_keywords(self):

        idl_test_procedure = idl.export_procedure("idl_test_procedure", return_arguments=[0, 1, 2, 3])
        a, b, c, d = idl_test_procedure(1.5, 2.5, 3.5, 4.5, key_b=True)
        self.assertEqual(a, 2000, "Argument a was not correctly returned.")
        self.assertEqual(b, 3000, "Argument b was not correctly returned.")
        self.assertEqual(c, 4000, "Argument c was not correctly returned.")
        self.assertEqual(d, 0.0, "Argument d was not correctly returned.")
