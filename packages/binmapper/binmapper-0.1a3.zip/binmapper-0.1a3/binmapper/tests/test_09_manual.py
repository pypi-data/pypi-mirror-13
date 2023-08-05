import unittest
import binmapper
import textwrap



class testManual(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_basic_types(self):
        r_uint8 = binmapper.types.uint8(1)
        r_uint16 = binmapper.types.uint16(1)
        r_uint32 = binmapper.types.uint32(1)
        r_sint8 = binmapper.types.sint8(1)
        r_sint16 = binmapper.types.sint16(1)
        r_sint32 = binmapper.types.sint32(1)
        r_float = binmapper.types.float(1.0)
        #r_string = binmapper.types.string(1)
        self.assertEqual(r_uint8.value, 1)
        self.assertEqual(r_uint16.value, 1)
        self.assertEqual(r_uint32.value, 1)
        self.assertEqual(r_sint8.value, 1)
        self.assertEqual(r_sint16.value, 1)
        self.assertEqual(r_sint32.value, 1)
        self.assertEqual(r_float.value, 1.0)

    def test_02_expr(self):
        expr = binmapper.types.Expr(3)
        self.assertEqual(expr.eval(), 3)

    def xtest_03_expr(self):
        expr = binmapper.types.Expr1("input")
        self.assertEqual(expr.eval(), 3)

    def test_04_array_fill(self):
        array_uint8 = binmapper.types.array(binmapper.types.uint8, binmapper.types.Expr(3))
        array_uint8.fill(3, 0x01)
        self.assertEqual(len(array_uint8.value), 3)
        self.assertEqual(array_uint8[0].value, 1)
        self.assertEqual(array_uint8[1].value, 1)
        self.assertEqual(array_uint8[2].value, 1)


if __name__ == '__main__':
    unittest.main()
