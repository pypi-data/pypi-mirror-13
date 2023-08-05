import unittest
import binmapper
import textwrap
from io import StringIO
from binmapper.parser.lexical_analyser import LexicalAnalyser


class testWisent(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_malformed(self):
        definition = u"""\
        bintype Bin: field: uint8
        """
        definition = textwrap.dedent(definition)
        with self.assertRaises(SystemExit) as cm:
            binmapper.compile(definition)

    def test_02_maxerr(self):
        definition = u"""\
        bintype Bin: field: uint8
        """
        definition = textwrap.dedent(definition)

        definition = StringIO(definition)
        lexer = LexicalAnalyser(max_err = 0)
        tokens = lexer.parse(definition.readline)
        with self.assertRaises(SystemExit) as cm:
            ast = lexer.safe_parse(tokens)  # Abstract syntax tree

    def test_03_good(self):
        definition = u"""\
        bintype Bin:
            field: uint8
        """
        definition = textwrap.dedent(definition)
        tbin = binmapper.compile(definition)
        self.assertIn('Bin', dir(tbin))

if __name__ == '__main__':
    unittest.main()
