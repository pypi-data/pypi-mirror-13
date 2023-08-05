import unittest
import binmapper
import textwrap
import io


class testUserType(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_usertype(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype BinX:
            field: uint8
        bintype Bin:
            field: BinX
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        self.assertIn('Bin', dir(tbin))
        self.assertIn('BinX', dir(tbin))

    def test_02_basic_types(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype BinX:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
        bintype Bin:
            field: BinX
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")
        bin.parse(input)
        self.assertEqual(bin.field.field_uint8.value, 1)
        self.assertEqual(bin.field.field_uint16.value, 2)
        self.assertEqual(bin.field.field_uint32.value, 3)
        self.assertEqual(bin.field.field_sint8.value, -1)
        self.assertEqual(bin.field.field_sint16.value, -2)
        self.assertEqual(bin.field.field_sint32.value, -3)
        self.assertEqual(bin.field.field_float.value, 2.0)

if __name__ == '__main__':
    unittest.main()
