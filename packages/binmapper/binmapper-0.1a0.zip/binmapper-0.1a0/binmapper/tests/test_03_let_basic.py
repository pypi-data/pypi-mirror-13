import unittest
import binmapper
import textwrap
import io


class testLetFieldBasic(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_letfield(self):
        binmapper.enable_debug()
        definition = u"""\
        bintype Bin:
            &let let_field : uint8 = 1
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        bin = tbin.Bin()
        input = io.BytesIO("")
        bin.parse(input)
        self.assertEqual(bin.let_field.value, 1)


if __name__ == '__main__':
    unittest.main()
