import unittest
import binmapper
import textwrap
import io


class testBasicTypes(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_bintype(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field: uint8
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        self.assertIn('Bin', dir(tbin))

    def test_02_basic_types(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")
        print len(input.getvalue())
        bin.parse(input)
        self.assertEqual(bin.field_uint8.value, 1)
        self.assertEqual(bin.field_uint16.value, 2)
        self.assertEqual(bin.field_uint32.value, 3)
        self.assertEqual(bin.field_sint8.value, -1)
        self.assertEqual(bin.field_sint16.value, -2)
        self.assertEqual(bin.field_sint32.value, -3)
        self.assertEqual(bin.field_float.value, 2.0)

    def test_03_basic_types_byteorder(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8 byteorder=bigendian
            field_uint16: uint16 byteorder=bigendian
            field_uint32: uint32 byteorder=bigendian
            field_sint8:  sint8 byteorder=bigendian
            field_sint16: sint16 byteorder=bigendian
            field_sint32: sint32 byteorder=bigendian
            field_float: float byteorder=bigendian
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x40\x00\x00\x00")
        bin.parse(input)
        self.assertEqual(bin.field_uint8.value, 1)
        self.assertEqual(bin.field_uint16.value, 512)
        self.assertEqual(bin.field_uint32.value, 50331648)
        self.assertEqual(bin.field_sint8.value, -1)
        self.assertEqual(bin.field_sint16.value, -257)
        self.assertEqual(bin.field_sint32.value, -33554433)
        self.assertEqual(bin.field_float.value, 2.0)

    def test_04_basic_types_class_byteorder(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
            &byteorder: bigendian
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x40\x00\x00\x00")
        bin.parse(input)
        self.assertEqual(bin.field_uint8.value, 1)
        self.assertEqual(bin.field_uint16.value, 512)
        self.assertEqual(bin.field_uint32.value, 50331648)
        self.assertEqual(bin.field_sint8.value, -1)
        self.assertEqual(bin.field_sint16.value, -257)
        self.assertEqual(bin.field_sint32.value, -33554433)
        self.assertEqual(bin.field_float.value, 2.0)

    def test_05_basic_types_user_byteorder(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
            &byteorder: bigendian
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin(byteorder = 'littleendian')
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")
        bin.parse(input)
        self.assertEqual(bin.field_uint8.value, 1)
        self.assertEqual(bin.field_uint16.value, 2)
        self.assertEqual(bin.field_uint32.value, 3)
        self.assertEqual(bin.field_sint8.value, -1)
        self.assertEqual(bin.field_sint16.value, -2)
        self.assertEqual(bin.field_sint32.value, -3)
        self.assertEqual(bin.field_float.value, 2.0)

    def test_06_string(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_string:  string[3]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x41\x42\x43")
        bin.parse(input)
        self.assertEqual(bin.field_string.value, "ABC")

    def test_07_basic_types_store(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")
        bin.parse(input)
        output = io.BytesIO("")
        bin.store(output)
        self.assertEqual(output.getvalue(), "\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")

    def test_08_string_store(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_string:  string[3]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x41\x42\x43")
        bin.parse(input)
        output = io.BytesIO("")
        bin.store(output)
        self.assertEqual(output.getvalue(), "ABC")

    def test_09_basic_types_bytesize(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_uint8:  uint8
            field_uint16: uint16
            field_uint32: uint32
            field_sint8:  sint8
            field_sint16: sint16
            field_sint32: sint32
            field_float: float
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40")
        bin.parse(input)
        self.assertEqual(bin.field_uint8.byte_size(), 1)
        self.assertEqual(bin.field_uint16.byte_size(), 2)
        self.assertEqual(bin.field_uint32.byte_size(), 4)
        self.assertEqual(bin.field_sint8.byte_size(), 1)
        self.assertEqual(bin.field_sint16.byte_size(), 2)
        self.assertEqual(bin.field_sint32.byte_size(), 4)
        self.assertEqual(bin.field_float.byte_size(), 4)

    def test_10_string_byte_size(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_string:  string[3]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x41\x42\x43")
        bin.parse(input)
        self.assertEqual(bin.field_string.byte_size(), 3)

    def test_11_comment(self):
        definition = u"""\
        #comment1
        bintype Bin: #comment2
            #comment3
            field1: uint8
            #comment4
            field2: uint8 #comment5
            #comment6
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        self.assertIn('Bin', dir(tbin))


if __name__ == '__main__':
    unittest.main()
