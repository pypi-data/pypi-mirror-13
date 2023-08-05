import unittest
import binmapper
import textwrap
import io


class testArrayType(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_array(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[2]
            field_array_uint16:  uint16[2]
            field_array_uint32:  uint32[2]
            field_array_sint8:   sint8[2]
            field_array_sint16:  sint16[2]
            field_array_sint32:  sint32[2]
            field_array_float:  float[2]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO(
            "\x01\x02\x01\x00\x02\x00\x01\x00\x00\x00\x02\x00\x00\x00\xFF\xFE\xFF\xFF\xFE\xFF\xFF\xFF\xFF\xFF\xFE\xFF\xFF\xFF\x00\x00\x00\x40\x00\x00\x00\x40")
        bin.parse(input)
        self.assertEqual(bin.field_array_uint8[0].value, 1)
        self.assertEqual(bin.field_array_uint8[1].value, 2)
        self.assertEqual(bin.field_array_uint16[0].value, 1)
        self.assertEqual(bin.field_array_uint16[1].value, 2)
        self.assertEqual(bin.field_array_uint32[0].value, 1)
        self.assertEqual(bin.field_array_uint32[1].value, 2)
        self.assertEqual(bin.field_array_sint8[0].value, -1)
        self.assertEqual(bin.field_array_sint8[1].value, -2)
        self.assertEqual(bin.field_array_sint16[0].value, -1)
        self.assertEqual(bin.field_array_sint16[1].value, -2)
        self.assertEqual(bin.field_array_sint32[0].value, -1)
        self.assertEqual(bin.field_array_sint32[1].value, -2)
        self.assertEqual(bin.field_array_float[0].value, 2.0)
        self.assertEqual(bin.field_array_float[1].value, 2.0)

    def test_02_array_variable_length(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_len: uint16
            field_array_uint16:   uint16[ (-((~(int(field_array_len + 2 ** (((5 + 10 - 2 / 2) % (0.5*16)) // 3)) << 4)) >> 4)) - 1]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint16), 5)
        self.assertEqual(bin.field_array_uint16[0].value, 1)
        self.assertEqual(bin.field_array_uint16[1].value, 2)
        self.assertEqual(bin.field_array_uint16[2].value, 3)
        self.assertEqual(bin.field_array_uint16[3].value, 4)
        self.assertEqual(bin.field_array_uint16[4].value, 5)

    def test_02_array_rest(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[] &restofdata
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02\x03\x04\x05")
        bin.parse(input)
        self.assertEqual(bin.field_array_uint8[0].value, 1)
        self.assertEqual(bin.field_array_uint8[1].value, 2)
        self.assertEqual(bin.field_array_uint8[2].value, 3)
        self.assertEqual(bin.field_array_uint8[3].value, 4)
        self.assertEqual(bin.field_array_uint8[4].value, 5)

    def test_03_array_until(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[] &until ($input != 0)
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x03\x02\x00\x04\x05")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint8), 3)
        self.assertEqual(bin.field_array_uint8[0].value, 3)
        self.assertEqual(bin.field_array_uint8[1].value, 2)
        self.assertEqual(bin.field_array_uint8[2].value, 0)

    def test_03_array_until_ext0(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[] &until ( $input +  $input )
        """
        definition = textwrap.dedent(definition)
        #import rpdb2; rpdb2.start_embedded_debugger("1")
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x03\x02\x05\x04\x00")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint8), 5)

    def test_03_array_until_ext1(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[] &until ( ($input != 0 and $input != 5) or not (1 == 1))
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x03\x02\x05\x04\x00")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint8), 3)
        self.assertEqual(bin.field_array_uint8[0].value, 3)
        self.assertEqual(bin.field_array_uint8[1].value, 2)
        self.assertEqual(bin.field_array_uint8[2].value, 5)

    def test_04_array_store(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[2]
            field_array_uint16:  uint16[2]
            field_array_uint32:  uint32[2]
            field_array_sint8:   sint8[2]
            field_array_sint16:  sint16[2]
            field_array_sint32:  sint32[2]
            field_array_float:  float[2]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO(
            "\x01\x02\x01\x00\x02\x00\x01\x00\x00\x00\x02\x00\x00\x00\xFF\xFE\xFF\xFF\xFE\xFF\xFF\xFF\xFF\xFF\xFE\xFF\xFF\xFF\x40\x00\x00\x00\x40\x00\x00\x00")
        bin.parse(input)
        output = io.BytesIO("")
        bin.store(output)
        self.assertEqual(
            output.getvalue(),
            "\x01\x02\x01\x00\x02\x00\x01\x00\x00\x00\x02\x00\x00\x00\xFF\xFE\xFF\xFF\xFE\xFF\xFF\xFF\xFF\xFF\xFE\xFF\xFF\xFF\x40\x00\x00\x00\x40\x00\x00\x00")

    def test_04_array_byte_size(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[2]
            field_array_uint16:  uint16[2]
            field_array_uint32:  uint32[2]
            field_array_sint8:   sint8[2]
            field_array_sint16:  sint16[2]
            field_array_sint32:  sint32[2]
            field_array_float:  float[2]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO(
            "\x01\x02\x01\x00\x02\x00\x01\x00\x00\x00\x02\x00\x00\x00\xFF\xFE\xFF\xFF\xFE\xFF\xFF\xFF\xFF\xFF\xFE\xFF\xFF\xFF\x40\x00\x00\x00\x40\x00\x00\x00")
        bin.parse(input)
        self.assertEqual(bin.field_array_uint8.byte_size(), 2)
        self.assertEqual(bin.field_array_uint16.byte_size(), 4)
        self.assertEqual(bin.field_array_uint32.byte_size(), 8)
        self.assertEqual(bin.field_array_sint8.byte_size(), 2)
        self.assertEqual(bin.field_array_sint16.byte_size(), 4)
        self.assertEqual(bin.field_array_sint32.byte_size(), 8)
        self.assertEqual(bin.field_array_float.byte_size(), 8)
        self.assertEqual(bin.byte_size(), 36)

    def test_09_padding(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint16:   uint16[] &until ($input != 0)
            pad: padding align field_array_uint16 4
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x03\x00\x02\x00\x00\x00\x04\x05")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint16), 3)
        self.assertEqual(len(bin.pad), 2)

    def test_10_padding_zero(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint8:   uint8[] &until ($input != 0)
            pad: padding align field_array_uint8 4
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x03\x02\x03\x00\x04\x05")
        bin.parse(input)
        self.assertEqual(len(bin.field_array_uint8), 4)
        self.assertEqual(len(bin.pad), 0)

    def test_11_array_and_padding_store(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            field_array_uint16:  uint16[3]
            field_pad:  padding align field_array_uint16 4
            field_array_sint8:   sint16[2]
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x00\x02\x00\x03\x00\xFF\xFF\xFE\xFF\xFE\xFF")
        bin.parse(input)
        bin.field_array_uint16 = binmapper.types.array(binmapper.types.uint8, binmapper.types.Expr(3))
        bin.field_array_uint16.fill(3, 0x01)
        output = io.BytesIO("")
        bin.store(output)
        self.assertEqual(output.getvalue(), "\x01\x01\x01\xFF\xFE\xFF\xFE\xFF")

if __name__ == '__main__':
    unittest.main()
