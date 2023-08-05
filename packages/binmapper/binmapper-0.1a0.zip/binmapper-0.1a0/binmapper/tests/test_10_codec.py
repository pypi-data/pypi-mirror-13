import unittest
import textwrap
import StringIO
import io

import binmapper

@unittest.skip("developing")
class testCodec(unittest.TestCase):

    def setUp(self):
        pass

    def disabled_test_01_codec(self):
        #binmapper.enable_debug()
        definition = u"""\
        # encoding: binmapper
        import io
        
        bintype BinX:
            field_uint16: uint16
            
        bintype Bin:
            field: BinX
        
        def test():
            bin = Bin()
            bin.parse(io.BytesIO("\x01\x02\x00\x03\x00\x00\x00\xFF\xFE\xFF\xFD\xFF\xFF\xFF\x00\x00\x00\x40"))
            if bin.field.field_uint16.value == 2:
                return True
            return False
        """
        definition = textwrap.dedent(definition)
        with io.open("./temp/definition.py",'w+', encoding = 'utf-8') as f:
            f.write(definition)
        import binmapper.codec.register    
        import binmapper.tests.temp.definition
        print dir(binmapper.tests.temp.definition)
        
        self.assertEqual(binmapper.tests.temp.definition.test(), True)
        
if __name__ == '__main__':
    unittest.main()
