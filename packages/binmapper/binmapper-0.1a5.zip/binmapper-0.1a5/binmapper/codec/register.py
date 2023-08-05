# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" binmapper encoding codec.

"""

import codecs
import encodings
import io
import os.path
import linecache
import sys
import traceback
import linecache
    
import binmapper.parser.helper

class binmapperStreamReader(encodings.utf_8.StreamReader):

    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        data = binmapper.parser.helper.transform(self.stream.readline)
        virtual_name = binmapper.parser.helper.save_code_listing_in_memory(self.stream.name, data)
        self.stream = io.BytesIO(data)
        self.stream.name = virtual_name
        #print data

def search_function(encoding):
    if encoding != 'binmapper':
        return None
    # Assume utf8 encoding
    
    utf8 = encodings.search_function('utf8')

    return codecs.CodecInfo(
        name = 'binmapper',
        encode = utf8.encode,
        decode = utf8.decode,  # binmapper_decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = utf8.incrementaldecoder,  # binmapperIncrementalDecoder,
        streamreader = binmapperStreamReader,
        streamwriter = utf8.streamwriter)

##########################################
# correct source filename for proper debug
'''
def fake_getline(filename, lineno, module_globals=None):
    global stream_filename, stream_filepath
    # print filename
    import os.path
    import linecache
    ret = ""
    if filename == os.path.join(stream_filepath, stream_filename):
        filename = os.path.join(stream_filepath, 'binmapper-' + stream_filename)
        ret = linecache.orig_getline(filename, 1, module_globals)
        ret = ret.split('\n')[lineno - 2]
    else:
        ret = linecache.orig_getline(filename, lineno, module_globals)

    return ret

###########################################
'''

def init():
    codecs.register(search_function)
    binmapper.parser.helper.enable_debug()

init()

