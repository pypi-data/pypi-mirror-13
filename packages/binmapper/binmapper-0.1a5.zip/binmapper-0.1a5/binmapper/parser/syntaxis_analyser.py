# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Syntaxis analyser for binmapper DSL.

"""

from binmapper.parser import syntaxis_types

# tree {token, type, start, end, line, value}

class SyntaxisAnalyser(object):

    def __init__(self):
        #self.decls = []
        self.cur_decl = None

    def xeval(self, tree):
        if tree[0] == 'single_input':
            return self.xeval(tree[1])

        elif tree[0] == 'compound_stmt':
            compound_stmt = syntaxis_types.CompoundStmt()
            for t in tree[1:]:
                decl = self.xeval(t)
                compound_stmt.decls.append(decl)
            return compound_stmt

        elif tree[0] == 'class':
            self.cur_decl = syntaxis_types.ClassDecl()
            self.cur_decl.id = self.xeval(tree[1])
            for t in tree[2:]:
                self.xeval(t)  # include class_scope, newline, indents
            return self.cur_decl

        elif tree[0] == 'classdef':
            cid = self.xeval(tree[2])
            return cid

        elif tree[0] == 'class_scope':
            for t in tree[1:]:
                # TODO: resolve mix Attribute and LetField
                if t[0] == "class_attribute":
                    class_attribute = self.xeval(t)
                    if isinstance(class_attribute, syntaxis_types.Attribute):
                        self.cur_decl.attributes.append(class_attribute)
                    elif isinstance(class_attribute, syntaxis_types.LetField):
                        self.cur_decl.let_fields.append(class_attribute)
                else:
                    field = self.xeval(t)
                    self.cur_decl.fields.append(field)
            return None

        elif tree[0] == 'class_field':
            # test for identity ?
            field = syntaxis_types.Field()
            field.id = self.xeval(tree[1])
            field_type = self.xeval(tree[3])
            field.type = field_type
            field.attributes = field_type.attributes
            return field

        elif tree[0] == 'class_attribute':
            attr = self.xeval(tree[2])
            return attr

        elif tree[0] == 'class_attribute_spec':
            attr = self.xeval(tree[1])
            return attr

        elif tree[0] == 'class_attribute_byteorder':
            attr = syntaxis_types.Attribute()
            attr.type = "byteorder"  # syntaxis_types.AttributeType.byteorder
            attr.expr.value = self.xeval(tree[3])
            return attr

        elif tree[0] == 'class_let_field':
            let_field = syntaxis_types.LetField()
            let_field.id = self.xeval(tree[2])
            field_type = self.xeval(tree[4])
            let_field.type = field_type
            let_field.attributes = field_type.attributes
            let_field.expr.value = self.xeval(tree[6])
            return let_field

        elif tree[0] == 'field_byteorder_attribute':
            attr = syntaxis_types.Attribute()
            attr.type = "byteorder"  # syntaxis_types.AttributeType.byteorder
            attr.expr.value = tree[3][5]
            return attr

        elif tree[0] == 'field_type':
            field_type = self.xeval(tree[1])
            for t in tree[2:]:
                attr = self.xeval(t)
                field_type.attributes.append(attr)
            return field_type

        elif tree[0] == 'complex_type':
            ttype = self.xeval(tree[1])
            return ttype

        elif tree[0] == 'basic_type':
            ttype = syntaxis_types.BasicSynType()
            ttype.type_str = tree[1][5]
            return ttype

        elif tree[0] == 'user_type':
            ttype = syntaxis_types.UserSynType()
            ttype.type_str = tree[1][5]
            return ttype

        elif tree[0] == 'array_type':
            element_type = self.xeval(tree[1])
            if element_type.type_str == "string":
                array_type = syntaxis_types.StringSynType()
            else:
                array_type = syntaxis_types.ArraySynType()
            array_type.element_type = element_type

            attr_pos = 4
            if tree[3][0] != "]":
                array_type.length = syntaxis_types.Expr(self.xeval(tree[3]))
                attr_pos = 5
            for t in tree[attr_pos:]:
                attr = self.xeval(t)
                array_type.attributes.append(attr)

            return array_type

        elif tree[0] == 'pad_type':
            pad_type = syntaxis_types.PadSynType()
            pad_type.align_base = self.xeval(tree[3])
            pad_type.align_mod = self.xeval(tree[4])
            pad_type.attributes = []
            return pad_type

        elif tree[0] == 'rest_attribute':
            attr = syntaxis_types.Attribute()
            attr.type = "rest"  # syntaxis_types.AttributeType.rest
            return attr

        elif tree[0] == 'until_attribute':
            attr = syntaxis_types.Attribute()
            attr.type = "until"  # syntaxis_types.AttributeType.until
            attr.expr = syntaxis_types.Expr1(self.xeval(tree[4]))  # using 1 parameter
            #attr.expr.value = self.xeval(tree[4])
            return attr

        elif tree[0] == 'test':
            return self.xeval(tree[1])
        elif tree[0] == 'or_test':
            expr = self.xeval(tree[1])
            if len(tree) > 3:
                for t in tree[3::2]:
                    expr = expr + " or " + self.xeval(t)
            return expr
        elif tree[0] == 'and_test':
            expr = self.xeval(tree[1])
            if len(tree) > 3:
                for t in tree[3::2]:
                    expr = expr + " and " + self.xeval(t)
            return expr
        elif tree[0] == 'not_test':
            if len(tree) == 3:
                return "not " + self.xeval(tree[2])
            else:
                return self.xeval(tree[1])
        elif tree[0] == 'comparison':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == 'comp_op':
            return tree[1][0]
        elif tree[0] == 'expr':
            expr = self.xeval(tree[1])
            if len(tree) > 3:
                for t in tree[3::2]:
                    expr = expr + " | " + self.xeval(t)
            return expr
        elif tree[0] == 'xor_expr':
            expr = self.xeval(tree[1])
            if len(tree) > 3:
                for t in tree[3::2]:
                    expr = expr + " ^ " + self.xeval(t)
            return expr
        elif tree[0] == 'and_expr':
            expr = self.xeval(tree[1])
            if len(tree) > 3:
                for t in tree[3::2]:
                    expr = expr + " & " + self.xeval(t)
            return expr
        elif tree[0] == 'shift_expr':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == '<<' or tree[0] == '>>':
            return tree[0]
        elif tree[0] == 'func_expr':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == 'arith_expr':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == '+' or tree[0] == '-':
            return tree[0]
        elif tree[0] == 'term':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == '*' or tree[0] == '/' or tree[0] == '%' or tree[0] == '//':
            return tree[0]
        elif tree[0] == 'factor':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == '~' or tree[0] == '**':
            return tree[0]
        elif tree[0] == 'power':
            expr = self.xeval(tree[1])
            for t in tree[2:]:
                expr = expr + self.xeval(t)
            return expr
        elif tree[0] == 'atom':
            # if tree[1][0] == '$':
            #    return 'input' #+ xeval(tree[2])[0]
            atom = self.xeval(tree[1])
            if tree[1][0] == 'name':
                atom = "id2obj(id_self).{0}.value".format(atom)
            return atom
        elif tree[0] == 'keyid':
            value = tree[2][5]  # TODO: this return "input" needsome other
            return value
        elif tree[0] == 'str':
            value = tree[1][5]
            return value
        elif tree[0] == 'number':
            value = tree[1][5]  # int ?
            return value
        elif tree[0] == 'name':
            value = tree[1][5]
            return value
        elif tree[0] == 'func':
            func = tree[1][5]
            return func
        elif tree[0] == 'T_LITTLEENDIAN':
            return "littleendian"
        elif tree[0] == 'T_BIGENDIAN':
            return "bigendian"
        elif tree[0] == '(':
            return "("
        elif tree[0] == ')':
            return ")"

            # return (tree[1][5],"",0)
