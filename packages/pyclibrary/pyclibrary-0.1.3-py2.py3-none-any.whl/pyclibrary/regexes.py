# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by PyCLibrary Authors, see AUTHORS for more details.
#
# Distributed under the terms of the MIT/X11 license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Useful regexes for analysing C files.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

hex_prefix = '0[xX]'
hex_digits = '[0-9a-fA-F]+'
bin_prefix = '0[bB]'
bin_digits = '[01]+'

# integer constants (K&R2: A.2.5.1)
int_suffix_opt = r'(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
decimal_int = '(0'+int_suffix_opt+')|([1-9][0-9]*'+int_suffix_opt+')'
octal_int = '[+-]?0[0-7]*'+int_suffix_opt
hex_int = hex_prefix+hex_digits+int_suffix_opt
bin_int = bin_prefix+bin_digits+int_suffix_opt

integer = decimal_int | octal_int | hex_int | bin_int

number = integer

# character constants (K&R2: A.2.5.2)
# Note: a-zA-Z and '.-~^_!=&;,' are allowed as escape chars to support #line
# directives with Windows paths as filenames (..\..\dir\file)
# For the same reason, decimal_escape allows all digit sequences. We want to
# parse all correct code, even if it means to sometimes parse incorrect
# code.
#
simple_escape = r"""([a-zA-Z._~!=&\^\-\\?'"])"""
decimal_escape = r"""(\d+)"""
hex_escape = r"""(x[0-9a-fA-F]+)"""
bad_escape = r"""([\\][^a-zA-Z._~^!=&\^\-\\?'"x0-7])"""

escape_sequence = r"""(\\("""+simple_escape+'|'+decimal_escape+'|'+hex_escape+'))'
cconst_char = r"""([^'\\\n]|"""+escape_sequence+')'
char_const = "'"+cconst_char+"'"
wchar_const = 'L'+char_const
unmatched_quote = "('"+cconst_char+"*\\n)|('"+cconst_char+"*$)"
bad_char_const = r"""('"""+cconst_char+"""[^'\n]+')|('')|('"""+bad_escape+r"""[^'\n]*')"""

# string literals (K&R2: A.2.6)
string_char = r"""([^"\\\n]|"""+escape_sequence+')'
string_literal = '"'+string_char+'*"'
wstring_literal = 'L'+string_literal
bad_string_literal = '"'+string_char+'*'+bad_escape+string_char+'*"'

# floating constants (K&R2: A.2.5.3)
exponent_part = r"""([eE][-+]?[0-9]+)"""
fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
floating_constant = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))[FfLl]?)'
binary_exponent_part = r'''([pP][+-]?[0-9]+)'''
hex_fractional_constant = '((('+hex_digits+r""")?\."""+hex_digits+')|('+hex_digits+r"""\.))"""
hex_floating_constant = '('+hex_prefix+'('+hex_digits+'|'+hex_fractional_constant+')'+binary_exponent_part+'[FfLl]?)'