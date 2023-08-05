# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Types for using with binmapper parser.

"""

import struct


def adopt_byteorder(byteorder_string):
    byteorder_symbol = "<"
    if byteorder_string == "littleendian":
        byteorder_symbol = "<"
    elif byteorder_string == "bigendian":
        byteorder_symbol = ">"
    return byteorder_symbol

def unpack(buffer, vtype, byteorder = None, length = None):
    byteorder = adopt_byteorder(byteorder) if byteorder != None else ""
    length = str(length) if length != None else ""
    return struct.unpack(byteorder + length + vtype, buffer)[0]

def pack(vtype, value, byteorder = None, length = None):
    byteorder = adopt_byteorder(byteorder) if byteorder != None else ""
    length = str(length) if length != None else ""
    return struct.pack(byteorder + length + vtype, value)

        
class Expr(object):

    def eval(self):
        return self.value()

    def __init__(self, value):
        if hasattr(value, "__name__") and value.__name__ == '<lambda>':
            # pre-evaluated value
            self.value = value
        else:
            # TODO: parse value in ast and make absolute references
            self.value = lambda: value


class Expr1(object):

    def eval(self, param1):
        return self.value(param1)

    def __init__(self, value):
        if hasattr(value, "__name__") and value.__name__ == '<lambda>':
            # pre-evaluated value
            self.value = value
        else:
            # TODO: parse value in ast and make absolute references
            self.value = lambda input: value


class BinType(object):

    def __init__(self, value, byteorder):
        if isinstance(byteorder, str):
            self.byteorder = Expr(byteorder)
        else:
            self.byteorder = byteorder
        self.value = value

    def byte_size(self, recursive = True):  # pragma: no cover
        raise Exception('Not implemented method')

    def parse(self, stream):  # pragma: no cover
        raise Exception('Not implemented method')

    def store(self, stream, sync = True):  # pragma: no cover
        raise Exception('Not implemented method')


class uint8(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 1

    def parse(self, stream):
        # print "parse uint8"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"B",self.byteorder.eval()))
        #self.value = int(struct.unpack("B", t)[0])
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store uint8"
        result = 0
        t = pack("B", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'uint8' with value '%d' in stream" % (self.value)
        return result


class uint16(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 2

    def parse(self, stream):
        # print "parse uint16"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"H",self.byteorder.eval()))
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store uint8"
        result = 0
        t = pack("H", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'uint8' with value '%d' in stream" % (self.value)
        return result

# TODO: optimise eval byteorder before every read or store ? cache ?


class uint32(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 4

    def parse(self, stream):
        # print "parse uint32"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"I",self.byteorder.eval()))
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store uint32"
        t = pack("I", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result is None:
        #    print "cannot write 'uint32' with value '%d' in stream" % (self.value)
        return result


class sint8(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 1

    def parse(self, stream):
        # print "parse sint8"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"b",self.byteorder.eval()))
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store sint8"
        result = 0
        t = pack("b", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'sint8' with value '%d' in stream" % (self.value)
        return result


class sint16(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 2

    def parse(self, stream):
        # print "parse sint16"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"h",self.byteorder.eval()))
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store sint16"
        result = 0
        t = pack("h", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'sint16' with value '%d' in stream" % (self.value)
        return result


class sint32(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 4

    def parse(self, stream):
        # print "parse sint32"
        t = stream.read(self.byte_size())
        self.value = int(unpack(t,"i",self.byteorder.eval()))
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store sint32"
        result = 0
        t = pack("i", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'sint32' with value '%d' in stream" % (self.value)
        return result


class float(BinType):

    def __init__(self, value = 0, byteorder = "littleendian"):
        BinType.__init__(self, value, byteorder)

    def byte_size(self, recursive = True):
        return 4

    def parse(self, stream):
        # print "parse float"
        t = stream.read(self.byte_size())
        self.value = unpack(t,"f",self.byteorder.eval()).__float__()
        return self.byte_size()

    def store(self, stream, sync = True):
        # print "store float"
        result = 0
        t = pack("f", self.value,self.byteorder.eval())
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'float' with value '%f' in stream" % (self.value)
        return result


class string(BinType):

    def __init__(self, size, value = ""):
        BinType.__init__(self, value, None)
        self.size = size

    def byte_size(self, recursive = True):
        return len(self.value)

    def parse(self, stream):
        # print "parse string"
        length = self.__len__()
        t = stream.read(length)
        self.value = unpack(t,"s", length = length)
        return length

    def store(self, stream, sync = True):
        # print "store string"
        result = 0
        t = pack("s", self.value, length = len(self.value))
        result = stream.write(t)
        # if result == None:
        #    print "cannot write 'string' with value '%s' in stream" % (self.value)
        return result

    def __len__(self):
        return self.size.eval()

# TODO: optimize multi create element type ?


class array(BinType):

    def __init__(self, type, size, value = None, attrs = {}):
        if value is None:
            value = []  # workaround of 'feature': only one instance of [] created while evaluate 'def'
        BinType.__init__(self, value, attrs.get('byteorder') if attrs.get('byteorder') is not None else Expr(lambda: 'littleendian'))
        self.size = size
        self.type = type
        self.attrs = attrs
        self.append_size = 0

    def byte_size(self, recursive = True):
        result = 0
        if recursive:
            for i in self.value:
                result += i.byte_size(recursive)
        return result

    def parse(self, stream):
        # print "parse binarray"
        result = 0
        size = self.size.eval()

        if self.attrs.get('rest') is not None:
            append_size = 0
            error = False
            while not error:
                try:
                    elem = self.type(byteorder = self.byteorder)
                    result += elem.parse(stream)
                    self.append(elem)
                    append_size += 1  # because we cant change size in lambda
                except struct.error:
                    error = True
            self.size.value = lambda: append_size
            return result

        if self.attrs.get('until') is not None:
            ret_value = True
            append_size = 0
            while self.attrs.get('until').eval(ret_value):
                elem = self.type(byteorder = self.byteorder)
                result += elem.parse(stream)
                self.append(elem)
                append_size += 1  # because we cant change size in lambda
                ret_value = elem.value
            self.size.value = lambda: append_size
            return result

        for i in xrange(size):
            elem = self.type(byteorder = self.byteorder)
            result += elem.parse(stream)
            self.append(elem)

        return result

    def sync(self):  # synchronize array length with size in definition
        # UPDATE ALIGN PAD SIZE
        size = self.size.eval()
        diff_elem_count = size - len(self.value)
        if diff_elem_count > 0:
            self.fill(diff_elem_count, 0)
        elif diff_elem_count < 0:
            del self.value[diff_elem_count:]

    def store(self, stream, sync = True):
        # print "store binarray"
        if sync:
            self.sync()
        result = None
        for i in self.value:
            i.store(stream)
        return result

    def __getitem__(self, offset):
        #print('(indexing %s at %s)' % (self, offset))
        return self.value.__getitem__(offset)

    def append(self, value):
        fq_value_type = value.__module__ + "." + value.__class__.__name__
        fq_array_elem_type = self.type.__module__ + "." + self.type.__name__
        if fq_value_type != fq_array_elem_type:
            print "Warning! Trying append incorrect type '%s' to binarray with type '%s'" % (fq_value_type, fq_array_elem_type)

        self.value.append(value)

    def fill(self, count, value):
        for i in xrange(count):
            xval = value(i) if hasattr(value, '__call__') else value
            xtype = self.type(0, self.byteorder)
            xtype.value = xval
            self.append(xtype)

    def __len__(self):
        return self.size.eval()


class raw_array(BinType):

    def __init__(self):
        pass

    def parse(self, stream):
        pass
