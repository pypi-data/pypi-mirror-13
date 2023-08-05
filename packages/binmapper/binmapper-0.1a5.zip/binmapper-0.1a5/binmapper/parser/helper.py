# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" binmapper helper.

"""

import sys
import traceback
import imp
import __builtin__
import io

from binmapper.parser.lexical_analyser import LexicalAnalyser
from binmapper.parser.syntaxis_analyser import SyntaxisAnalyser
from binmapper.parser import dump


virtual_filepath = ""
virtual_filename = ""


def compile(definition):
    definition = io.StringIO(definition)
    out = transform(definition.readline)
    save_code_listing_in_memory("<binmapper-string>", out)
    binmapper_ = imp.new_module('binmapper_')
    bytecode = __builtin__.compile(out, "<binmapper-string>", "exec")
    exec bytecode in binmapper_.__dict__
    return binmapper_
    # python 3
    # mymodule = imp.new_module('mymodule')
    # exec(my_code, mymodule.__dict__)

def transform(readline):
    lexer = LexicalAnalyser()
    synparser = SyntaxisAnalyser()
    tokens = lexer.parse(readline)
    ast = lexer.safe_parse(tokens)  # Abstract syntax tree
    ir_tree = synparser.xeval(ast)  # intermediate representation
    #print (dump.dump_args(ir_tree))
    out = ir_tree.generate() + "\n"
    #print (out)
    return out.encode("utf-8")
##########################################
# save code listing in memory for debug
    
def save_code_listing_in_memory(real_filename, data):
    global virtual_filepath, virtual_filename
    import os.path
    head, tail = os.path.split(real_filename)
    virtual_filepath = head
    virtual_filename = tail
    virtual_name = os.path.join(virtual_filepath, 'binmapper-' + virtual_filename)
    import linecache
    linecache.cache[virtual_name] = len(data), None, [data], virtual_name
    return virtual_name
##########################################
# override print traceback

def custom_excepthook(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    # traceback.print_stack(file=sys.stdout)
    # print traceback.extract_tb(exc_traceback)


##########################################
# correct source filename for proper debug

def fake_getline(filename, lineno, module_globals=None):
    global virtual_filepath, virtual_filename
    import os.path
    import linecache
    ret = ""
    if filename == os.path.join(virtual_filepath, virtual_filename):
        filename = os.path.join(virtual_filepath, 'binmapper-' + virtual_filename)
        ret = linecache.orig_getline(filename, 1, module_globals)
        ret = ret.split('\n')[lineno - 1]  # lineno-2 for binmapper file
    else:
        ret = linecache.orig_getline(filename, lineno, module_globals)

    return ret

###########################################


def enable_debug():
    sys.excepthook = custom_excepthook
    import linecache
    if hasattr(linecache, 'orig_getline'):
        return  # we yet have patched linecache
    linecache.orig_getline = linecache.getline
    linecache.getline = fake_getline
    # del linecache, fake_getline
