# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Types using in syntaxis analysator.

"""

import marshal

from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader

from binmapper.parser.template_context import TemplateContext


class CompoundStmt(object):

    def __init__(self):
        self.decls = []

    def generate(self):
        loader = ChoiceLoader([
            PackageLoader('binmapper', 'parser/templates'),
            FileSystemLoader('./parser/templates')
        ])
        env = Environment(loader=loader)
        template = env.get_template('bintype.template')
        ctx = TemplateContext()

        ctx.start_capture("classes")
        for decl in self.decls:
            decl.generate(ctx)
            ctx.next_capture()
        ctx.end_capture()

        code = template.render(**ctx.raw())
        return code


class Decl(object):

    def __init__(self):
        self.id = None
        self.fields = []
        self.attributes = []
        self.let_fields = []


class ClassDecl(Decl):

    def generate(self, ctx):
        ctx.set(name = self.id)

        field_names_by_order = [field.id for field in self.fields]
        class_fields_by_order = "_field_names_by_order = {0}".format(
            '[' + ', '.join(field_names_by_order) + ']')
        ctx.set(class_fields_by_order = class_fields_by_order)

        ctx.start_capture("fields")
        for field in self.fields:
            field.generate(ctx)
            ctx.next_capture()
        ctx.end_capture()

        let_field_names_by_order = [field.id for field in self.let_fields]
        let_fields_by_order = "_let_field_names_by_order = {0}".format(
            '[' + ', '.join(let_field_names_by_order) + ']')
        ctx.set(let_fields_by_order = let_fields_by_order)

        ctx.start_capture("let_fields")
        for let_field in self.let_fields:
            let_field.generate(ctx)
            ctx.next_capture()
        ctx.end_capture()

        attrs = [attr for attr in self.attributes if attr.type == "byteorder"]
        class_byteorder = "binmapper.types.Expr(lambda: '{0}')".format(attrs[0].expr.eval()) if attrs else None
        set_class_byteorder = "self.byteorder = {0}".format(class_byteorder) if class_byteorder is not None else ''
        ctx.set(set_class_byteorder = set_class_byteorder)

        # test for identity ?

class Expr(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "binmapper.types.Expr( lambda: {0} )".format(self.value)

    def eval(self):
        return self.value

    def compile(self):
        expr_s = "binmapper.types.Expr( lambda: {0} )".format(self.value)
        expr_c = compile(expr_s, 'binmapper-expression', 'eval')
        expr_d = marshal.dumps(expr_c)
        return "eval(marshal.loads({0}))".format(expr_d)


class Expr1(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "binmapper.types.Expr1( lambda input: {0} )".format(self.value)

    def eval(self):
        return self.value


class Field(object):

    def __init__(self):
        self.id = None
        self.type = None
        self.attributes = []

    def generate(self, ctx):
        self.type.generate(ctx)
        attrs = [attr for attr in self.attributes if attr.type == "byteorder"]
        byteorder = "binmapper.types.Expr(lambda: '{0}')".format(attrs[0].expr.eval()) if attrs else 'byteorder'

        ctx.set(ctor = ctx.get("ctor").format(byteorder = byteorder))
        ctx.set(id = self.id)

        return None


class LetField(object):

    def __init__(self):
        self.id = None
        self.type = None
        self.attributes = []
        self.expr = Expr(None)

    def generate(self, ctx):
        self.type.generate(ctx)
        attrs = [attr for attr in self.attributes if attr.type == "byteorder"]
        byteorder = "binmapper.types.Expr(lambda: '{0}')".format(attrs[0].expr.eval()) if attrs else 'byteorder'

        ctx.set(ctor = ctx.get("ctor").format(byteorder = byteorder))
        ctx.set(value = repr(self.expr))
        ctx.set(id = self.id)

        return None

# class AttributeType:
#    byteorder = 1
#    until = 2
#    rest = 3


class Attribute(object):

    def __init__(self):
        self.type = None
        self.expr = Expr(None)

    def __repr__(self):
        return "{type!r} : {expr}".format(type = str(self.type), expr = repr(self.expr))


class SynType(object):

    def __init__(self):
        self.type_str = None
        self.attributes = []

    def attributes_repr(self):
        out = "{"
        for attr in self.attributes:
            out += repr(attr) + ", "
        out += "}"
        return out


class BasicSynType(SynType):

    def generate(self, ctx):
        ctx.set(suffix = "",
                ctor = "binmapper.types.{field_type}(byteorder = {byteorder})".format(
                    field_type = self.type_str,
                    byteorder = "{byteorder}"))


class UserSynType(SynType):

    def generate(self, ctx):
        ctx.set(suffix = "",
                ctor = "{field_type}(byteorder = {byteorder})".format(
                    field_type = self.type_str,
                    byteorder = "{byteorder}"))


class ArraySynType(SynType):

    def __init__(self):
        SynType.__init__(self)
        self.element_type = None
        self.length = Expr(0)

    def generate(self, ctx):
        package = "binmapper.types." if isinstance(self.element_type, BasicSynType) else ""
        ctx.set(suffix = "",
                ctor = "binmapper.types.array({package}{element_type}, {length}, attrs = {attrs})".format(
                    package = package,
                    element_type = self.element_type.type_str,
                    length = repr(self.length),
                    attrs = "{" + self.attributes_repr() + "}"))


class StringSynType(SynType):

    def __init__(self):
        SynType.__init__(self)
        self.element_type = None
        self.length = Expr(0)

    def generate(self, ctx):
        ctx.set(suffix = "",
                ctor = "binmapper.types.string({length})".format(length = repr(self.length)))


class PadSynType(SynType):

    def __init__(self):
        SynType.__init__(self)
        self.align_base = None
        self.align_mod = 0
        self.length = Expr(None)

    def generate(self, ctx):
        self.length.value = "{align_mod} - id2obj(id_self).{align_base}.byte_size() % {align_mod} \
            if id2obj(id_self).{align_base}.byte_size() %{align_mod} != 0 else 0 ".format(
                align_base = self.align_base,
                align_mod = self.align_mod)
        ctx.set(suffix = "",
                ctor = "binmapper.types.array(binmapper.types.uint8, {length})".format(
                    length = repr(self.length)))
