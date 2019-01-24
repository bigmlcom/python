# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2019 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tree utilities

This module stores auxiliar functions used in tree traversal and
code generators for the body of the local model plugins
"""

import re
import locale
import sys

from urlparse import urlparse
from unidecode import unidecode

from bigml.util import split

DEFAULT_LOCALE = 'en_US.UTF-8'
TM_TOKENS = 'tokens_only'
TM_FULL_TERM = 'full_terms_only'
TM_ALL = 'all'
TERM_OPTIONS = ["case_sensitive", "token_mode"]
ITEM_OPTIONS = ["separator", "separator_regexp"]
COMPOSED_FIELDS = ["text", "items"]
NUMERIC_VALUE_FIELDS = ["text", "items", "numeric"]

MAX_ARGS_LENGTH = 10

INDENT = u'    '

# Map operator str to its corresponding python operator
PYTHON_OPERATOR = {
    "<": "<",
    "<=": "<=",
    "=": "==",
    "!=": "!=",
    "/=": "!=",
    ">=": ">=",
    ">": ">"
}


# reserved keywords

CS_KEYWORDS = [
    "abstract", "as", "base", "bool", "break", "byte", "case",
    "catch", "char", "checked", "class", "const", "continue", "decimal",
    "default", "delegate", "do", "double", "else", "enum", "event", "explicit",
    "extern", "false", "finally", "fixed", "float", "for", "foreach", "goto",
    "if", "implicit", "in", "int", "interface", "internal", "is", "lock", "long",
    "namespace", "new", "null", "object", "operador", "out", "override",
    "params", "private", "protected", "public", "readonly", "ref", "return",
    "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string",
    "struct", "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong",
    "unchecked", "unsafe", "ushort", "using", "virtual", "void", "volatile",
    "while", "group", "set", "value"]

VB_KEYWORDS = [
    'addhandler', 'addressof', 'alias', 'and', 'andalso', 'as',
    'boolean', 'byref', 'byte', 'byval', 'call', 'case', 'catch', 'cbool',
    'cbyte', 'cchar', 'cdate', 'cdec', 'cdbl', 'char', 'cint', 'class', 'clng',
    'cobj', 'const', 'continue', 'csbyte', 'cshort', 'csng', 'cstr',
    'ctype', 'cuint', 'culng', 'cushort', 'date', 'decimal', 'declare',
    'default', 'delegate', 'dim', 'directcast', 'do', 'double', 'each',
    'else', 'elseif', 'end', 'endif', 'enum', 'erase', 'error', 'event',
    'exit', 'false', 'finally', 'for', 'friend', 'function', 'get',
    'gettype', 'getxmlnamespace', 'global', 'gosub', 'goto', 'handles',
    'if', 'implements', 'imports ', 'in', 'inherits', 'integer', 'interface',
    'is', 'isnot', 'let', 'lib', 'like', 'long', 'loop', 'me', 'mod', 'module',
    'mustinherit', 'mustoverride', 'mybase', 'myclass', 'namespace',
    'narrowing', 'new', 'next', 'not', 'nothing', 'notinheritable',
    'notoverridable', 'object', 'of', 'on', 'operator', 'option',
    'optional', 'or', 'orelse', 'overloads', 'overridable', 'overrides',
    'paramarray', 'partial', 'private', 'property', 'protected',
    'public', 'raiseevent', 'readonly', 'redim', 'rem', 'removehandler',
    'resume', 'return', 'sbyte', 'select', 'set', 'shadows', 'shared',
    'short', 'single', 'static', 'step', 'stop', 'string', 'structure',
    'sub', 'synclock', 'then', 'throw', 'to', 'true', 'try',
    'trycast', 'typeof', 'variant', 'wend', 'uinteger', 'ulong',
    'ushort', 'using', 'when', 'while', 'widening', 'with', 'withevents',
    'writeonly', 'xor', '#const', '#else', '#elseif', '#end', '#if'
]

JAVA_KEYWORDS = [
    "abstract", "continue", "for", "new", "switch", "assert", "default",
    "goto", "package", "synchronized", "boolean", "do", "if", "private",
    "this", "break", "double", "implements", "protected", "throw",
    "byte", "else", "import", "public", "throws", "case", "enum",
    "instanceof", "return", "transient", "catch", "extends", "int",
    "short", "try", "char", "final", "interface", "static", "void",
    "class", "finally", "long", "strictfp", "volatile", "const",
    "float", "native", "super", "while"
]

OBJC_KEYWORDS = [
    "auto", "BOOL", "break", "Class", "case", "bycopy", "char", "byref",
    "const", "id", "continue", "IMP", "default", "in", "do", "inout",
    "double", "nil", "else", "NO", "enum", "NULL", "extern", "oneway",
    "float", "out", "for", "Protocol", "goto", "SEL", "if", "self",
    "inline", "super", "int", "YES", "long", "@interface", "register",
    "@end", "restrict", "@implementation", "return", "@protocol",
    "short", "@class", "signed", "@public", "sizeof", "@protected",
    "static", "@private", "struct", "@property", "switch", "@try",
    "typedef", "@throw", "union", "@catch()", "unsigned", "@finally",
    "void", "@synthesize", "volatile", "@dynamic", "while", "@selector",
    "_Bool", "atomic", "_Complex", "nonatomic", "_Imaginery", "retain"
]

JS_KEYWORDS = [
    "break", "case", "catch", "continue", "debugger", "default", "delete",
    "do", "else", "finally", "for", "function", "if", "in", "instanceof",
    "new", "return", "switch", "this", "throw", "try", "typeof", "var",
    "void", "while", "with", "class", "enum", "export", "extends",
    "import", "super", "implements", "interface", "let", "package",
    "private", "protected", "public", "static", "yield", "null",
    "true", "const", "false"
]


PYTHON_KEYWORDS = [
    "and", "assert", "break", "class", "continue", "def", "del", "elif",
    "else", "except", "exec", "finally", "for", "from", "global", "if",
    "import", "in", "is", "lambda", "not", "or", "pass", "print", "raise",
    "return", "try", "while ", "Data", "Float", "Int", "Numeric", "Oxphys",
    "array", "close", "float", "int", "input", "open", "range", "type",
    "write", "zeros", "acos", "asin", "atan", "cos", "e", "exp", "fabs",
    "floor", "log", "log10", "pi", "sin", "sqrt", "tan"
]


def java_string(text):
    """Transforms string output for java, cs, and objective-c code

    """
    text = "%s" % text
    return text.replace("&quot;", "\"").replace("\"", "\\\"")


def python_string(text):
    """Transforms string output for python code

    """
    return repr(text.replace("&#39;", "\'"))


def ruby_string(text):
    """Transforms string output for ruby code

    """
    out = python_string(text)
    if isinstance(text, unicode):
        return out[1:]
    return out


def sort_fields(fields):
    """Sort fields by column_number but put together parents and children.

    """
    fathers = [(key, val) for key, val in
               sorted(fields.items(),
                      key=lambda k: k[1]['column_number'])
               if not 'auto_generated' in val]
    children = [(key, val) for key, val in
                sorted(fields.items(),
                       key=lambda k: k[1]['column_number'])
                if 'auto_generated' in val]
    children.reverse()
    fathers_keys = [father[0] for father in fathers]
    for child in children:
        try:
            index = fathers_keys.index(child[1]['parent_ids'][0])
        except ValueError:
            index = -1

        if index >= 0:
            fathers.insert(index + 1, child)
        else:
            fathers.append(child)
    return fathers


def slugify(name, reserved_keywords=None, prefix=''):
    """Translates a field name into a variable name.

    """
    if len(name) == 0:
        # case of empty name?
        return name

    name = unidecode(name).lower()
    name = re.sub(r'\W+', '_', name)
    if name[0].isdigit():
        name = "field_" + name
    if reserved_keywords:
        if name in reserved_keywords:
            name = prefix + name
    return name


def plural(text, num):
    """Pluralizer: adds "s" at the end of a string if a given number is > 1

    """
    return "%s%s" % (text, "s"[num == 1:])


def prefix_as_comment(comment_prefix, text):
    """Adds comment prefixes to new lines in comments

    """
    return text.replace('\n', '\n' + comment_prefix)


def to_camelcase(text, first_lower=True,
                 reserved_keywords=None, prefix='', suffix=''):
    """Returns the text in camelCase or CamelCase format

    """
    if len(text) == 0:
        # case of empty name?
        return text

    text = re.sub(r'\W+', ' ', text)
    if reserved_keywords:
        if text.lower() in reserved_keywords:
            text = prefix + text + suffix
    if ' ' in text:
        text = unidecode(text).lower()
        text = re.sub(r'\w+', lambda m: m.group(0).capitalize(), text)
        text = re.sub(r'\s+', '', text)
    elif text == text.upper():
        # if the text is a single word in caps, we turn it all into lowers
        text = text.lower()
    if text[0].isdigit():
        text = "Field" + text
    if first_lower:
        return text[0].lower() + text[1:]
    return text[0].upper() + text[1:]


def to_camel_cs(text, first_lower=True):
    """Returns the text in camelCase or CamelCase format for C#

    """
    return to_camelcase(text, first_lower=first_lower,
                        reserved_keywords=CS_KEYWORDS, prefix="@")


def to_camel_vb(text, first_lower=True):
    """Returns the text in camelCase or CamelCase format for Visual Basic

    """
    text = "v_" + text
    return to_camelcase(text, first_lower=first_lower,
                        reserved_keywords=VB_KEYWORDS, prefix="v ")


def to_camel_java(text, first_lower=True):
    """Returns the text in camelCase or CamelCase format for Java

    """
    return to_camelcase(text, first_lower=first_lower,
                        reserved_keywords=JAVA_KEYWORDS, suffix="_")


def to_camel_objc(text, first_lower=True):
    """Returns the text in camelCase or CamelCase format for objective-c

    """
    keywords = [keyword.lower() for keyword in OBJC_KEYWORDS]
    return to_camelcase(text, first_lower=first_lower,
                        reserved_keywords=keywords, suffix="_")


def to_camel_js(text, first_lower=True):
    """Returns the text in camelCase or CamelCase format for node.js

    """
    return to_camelcase(text, first_lower=first_lower,
                        reserved_keywords=JS_KEYWORDS, suffix="_")


def docstring_comment(model):
    """Returns the docstring describing the model.

    """
    docstring = (u"Predictor for %s from %s" % (
        model.tree.fields[model.tree.objective_id]['name'],
        model.resource_id))
    model.description = (unicode( \
        model.description).strip() \
        or u'Predictive model by BigML - Machine Learning Made Easy')
    return docstring


def java_class_definition(model):
    """Implements java class definition and doc comments

    """
    docstring = model.java_comment()
    field_obj = model.tree.fields[model.tree.objective_id]
    if not 'CamelCase' in field_obj:
        field_obj['CamelCase'] = to_camel_java(field_obj['name'], False)
    output = \
u"""
/**
*  %s
*  %s
*/
public class %s {
""" % (docstring,
       model.description.replace('\n', '\n *  '),
       field_obj['CamelCase'])
    return output


# This method is reused in core/excel/producer.py class
def signature_name_vb(text, model):
    """Returns the name of the function in Visual Basic for Applications

    """
    default_description = "Predictive model by BigML - Machine Learning Made Easy"
    obj_field_for_name = to_camel_vb(text, False).replace("V_", "")
    obj_field_for_name = obj_field_for_name.title()
    header = ""
    if model:
        header = u"""
'
' Predictor for %s from %s
' %s
'
""" % (model.tree.fields[model.tree.objective_id]['name'],
       model.resource_id,
       model.description if model.description else default_description)
    return ("Predict{0}".format(obj_field_for_name), header)


def localize(number):
    """Localizes `number` to show commas appropriately.

    """
    return locale.format("%d", number, grouping=True)


def is_url(value):
    """Returns True if value is a valid URL.

    """
    url = isinstance(value, basestring) and urlparse(value)
    return url and url.scheme and url.netloc and url.path


def print_distribution(distribution, out=sys.stdout):
    """ Prints distribution data

    """
    total = reduce(lambda x, y: x + y,
                   [group[1] for group in distribution])
    output = u""
    for group in distribution:
        output += u"    %s: %.2f%% (%d instance%s)\n" % ( \
            group[0],
            round(group[1] * 1.0 / total, 4) * 100,
            group[1],
            "" if group[1] == 1 else "s")
    out.write(output)
    out.flush()


def filter_nodes(nodes_list, ids=None, subtree=True):
    """Filters the contents of a nodes_list. If any of the nodes is in the
       ids list, the rest of nodes are removed. If none is in the ids list
       we include or exclude the nodes depending on the subtree flag.

    """
    if not nodes_list:
        return None
    nodes = nodes_list[:]
    if ids is not None:
        for node in nodes:
            if node.id in ids:
                nodes = [node]
                return nodes
    if not subtree:
        nodes = []
    return nodes


def missing_branch(children):
    """Checks if the missing values are assigned to a special branch

    """
    return any([child.predicate.missing for child in children])


def none_value(children):
    """Checks if the predicate has a None value

    """
    return any([child.predicate.value is None for child in children])


def one_branch(children, input_data):
    """Check if there's only one branch to be followed

    """
    missing = split(children) in input_data
    return (missing or missing_branch(children)
            or none_value(children))


def tableau_string(text):
    """Transforms to a string representation in Tableau

    """
    value = repr(text)
    if isinstance(text, unicode):
        return value[1:]
    return value
