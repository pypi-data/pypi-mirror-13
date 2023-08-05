# Copyright 2015 RedSkotina
# Licensed under the Apache License, Version 2.0

""" Lexical Analyser for binmapper DSL.

"""

import tokenize
import re

import binmapper.parser.grammar



class LexicalAnalyser(object):

    def __init__(self, max_err = None):
        self.p = binmapper.parser.grammar.Parser(max_err = max_err)

    def parse(self, readline):

        itokens = []
        tokens = tokenize.generate_tokens(readline)
        # print p.terminals
        is_bintype = False
        token_ignore = False
        while True:
            try:
                token = next(tokens)
                ttype, tvalue, tstart, tend, tline = token
                xvalue = tvalue
                # print "|",tvalue,"|"
                # print "--"
                # tokenize.generate_tokens dont handle some symbols
                if ttype == tokenize.ERRORTOKEN:
                    re_pattern = re.compile(r'[ \f\t]')
                    if re_pattern.match(tvalue):
                        continue  # skip
                    re_pattern = re.compile(r'\$')
                    if re_pattern.match(tvalue):
                        tokenize.tok_name[128] = 'DOLLAR'
                        ttype = 128

                if (("T_" + tvalue.upper()) in self.p.terminals):
                    xvalue = "T_" + tvalue.upper()
                elif ttype == tokenize.NAME:
                    xvalue = "T_NAME"
                elif ttype == tokenize.NEWLINE:
                    xvalue = "T_NEWLINE"
                elif ttype == tokenize.NL:
                    xvalue = "T_NEWLINE"
                elif ttype == tokenize.INDENT:
                    xvalue = "T_INDENT"
                elif ttype == tokenize.DEDENT:
                    xvalue = "T_DEDENT"
                elif ttype == tokenize.NUMBER:
                    xvalue = "T_NUMBER"
                elif ttype == tokenize.STRING:
                    xvalue = "T_STRING"
                elif ttype == tokenize.ENDMARKER:
                    break
                elif ttype == tokenize.COMMENT:
                    token_ignore = True

                # print tvalue
                # print "--"
                print ("type %s  \t value %s \t=> %s " % (
                    tokenize.tok_name[ttype], repr(tvalue), xvalue))
                if xvalue == 'T_BINTYPE':
                    is_bintype = True

                if is_bintype and not token_ignore:
                    itokens.append([xvalue, ttype, tstart, tend, tline, tvalue])

                token_ignore = False
                if xvalue == 'T_DEDENT':
                    is_bintype = False

            except (StopIteration, tokenize.TokenError):
                if str(tokenize.TokenError) != "":
                    print ("Error: " + str(tokenize.TokenError))
                break
        return itokens

    def safe_parse(self, readline):
        try:
            tree = self.p.parse(readline)
            return tree
        except self.p.ParseErrors as e:
            for token, expected in e.errors:
                if token[0] == self.p.EOF:
                    print ("unexpected end of file")
                    continue

                found = repr(token[0])
                if len(expected) == 1:
                    msg = "missing %s (found %s)" % (repr(expected[0]), found)
                else:
                    msg1 = "parse error before %s, " % found
                    l = sorted([repr(s) for s in expected])
                    msg2 = "expected one of " + ", ".join(l)
                    msg = msg1 + msg2
                print (msg)
                print (">>>> line, col: " + str(token[2]))
                print (">>>>" + str(token[4]))
                print ("    " + (token[2][1] - 1) * " " + "^")
            raise SystemExit(1)
