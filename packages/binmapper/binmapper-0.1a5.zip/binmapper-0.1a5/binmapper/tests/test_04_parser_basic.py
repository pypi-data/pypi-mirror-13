import unittest
import binmapper
import textwrap
import io


class testParserBasic(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_expr(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : uint8 = 2 * 2 + 2
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 6)

    def test_02_expr(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : uint8 = 2 * (2 + 2)
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 8)

    def test_03_expr(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : float = 6 + 2 ** (((5 + 10 - 2 / 2) % (0.5*16)) // 3)
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 10.0)

    def test_04_expr(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : uint8 = (-((~(int(1 + 2 ** (((5 + 10 - 2 / 2) % (0.5*16)) // 3)) << 4)) >> 4))
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 6)

    def test_04_expr(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : uint8 = (-((~(int(1 + 2 ** (((5 + 10 - 2 / 2) % (0.5*16)) // 3)) << 4)) >> 4)) | 3 ^ 1
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("\x01\x02")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 6)

if __name__ == '__main__':
    unittest.main()
