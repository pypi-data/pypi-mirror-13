# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Helper for dump object for debug target.

"""

import types
import inspect


def get_userdefined_members(obj):
    attrs = inspect.getmembers(obj, lambda x: not inspect.ismethod(x))
    user_attrs = [attr for attr in attrs if not(attr[0].startswith('__') and attr[0].endswith('__'))]
    return user_attrs


def get_class_name(obj):
    name = (hasattr(obj, '__class__') and obj.__class__.__name__ or type(obj).__name__)
    return name


def dump_args(obj, depth = 1, out = ""):
    if depth > 10:
        return "maximum recursion depth error"
    is_dict_type = lambda x: isinstance(x, (dict))
    is_list_type = lambda x: isinstance(x, (list, tuple))
    attrs = None
    is_array = False
    if is_dict_type(obj):
        attrs = [(k, v) for k, v in obj.iteritems()]
        lbracket = "{"
        rbracket = "}"
        is_array = True
    elif is_list_type(obj):
        attrs = [(obj.index(x), x) for x in obj]
        lbracket = "["
        rbracket = "]"
        is_array = True
    else:
        attrs = get_userdefined_members(obj)
    is_basic_type = lambda x: isinstance(x, (int, float, str, unicode, bool, types.NoneType, types.LambdaType))

    out = get_class_name(obj) + ":" + (" " + lbracket + rbracket if is_array and not obj else "") + "\n"

    out += 4 * depth * " " + lbracket + "\n" if is_array and obj else ""
    for key, value in attrs:
        if (is_basic_type(value)):
            out += 4 * depth * " " + str(key) + " = " + str(value) + "\n"
        else:
            out += 4 * depth * " " + str(key) + " = " + dump_args(value, depth + 1, out) + "\n"
    out += 4 * depth * " " + rbracket + "\n" if is_array and obj else ""
    return out
