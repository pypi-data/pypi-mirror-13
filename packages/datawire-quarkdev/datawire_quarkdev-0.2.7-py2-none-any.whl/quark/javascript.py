# Copyright 2015 datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from collections import OrderedDict
from .helpers import *
from ._metadata import __js_runtime_version__

## Packaging

def package(name, version, packages, srcs):
    files = OrderedDict()
    files.update(srcs)
    for path, readme in packages.items():
        files["%s/README.md" % "/".join(path)] = readme
        files["%s/package.json" % "/".join(path)] = """
{
    "name":"%s",
    "version":"%s",
    "dependencies": {
        "datawire-quark-core": "%s"
    }
}
        """ % (name, version, __js_runtime_version__)
    return files

def class_file(path, name, fname):
    if path:
        return "/".join(path + ["index.js"])
    else:
        return "%s.js" % fname

def function_file(path, name, fname):
    return class_file(path, name, fname)

def package_file(path, name, fname):
    return "/".join(path + [name, "index.js"])

def make_class_file(path, name):
    return Code(head='var _qrt = require("datawire-quark-core");\n')

def make_function_file(path, name):
    return make_class_file(path, name)

def make_package_file(path, name):
    return make_class_file(path, name)

def main(fname, common):
    return Code("var common = require('./%s');\n\ncommon.main();\n" % common)

## Naming and imports

SUBS = {"self": "this"}
def name(n):
    return SUBS.get(n, n)

def type(path, name, parameters):
    return ".".join(path + [name])

def import_(path, origin):
    qual = qualify(path, origin)
    if tuple(origin) + tuple(qual) == tuple(path):
        prefix = "./"
    else:
        prefix = "../"*len(origin)
    return "var %s = require('%s%s');\nexports.%s = %s;" % (qual[0], prefix, qual[0], qual[0], qual[0])

def qualify(package, origin):
    if package == origin: return []
    if not package: return []
    if not origin:
        return package
    elif package[:len(origin)] == origin:
        return package[len(origin):]
    else:
        return package

## Documentation

def doc(lines):
    return doc_helper(lines, "/**", " * ", " */")

## Comments

def comment(stuff):
    return "/* %s */\n" % stuff

## Class definition

def clazz(doc, abstract, clazz, parameters, base, interfaces, fields, constructors, methods):
    if base: fields = [base + ".prototype.__init_fields__.call(this);"] + fields

    result = "\n// CLASS %s\n" % clazz + doc
    result += "\n".join(constructors)
    if base:
        result += "_qrt.util.inherits(%s, %s);\n" % (clazz, base)

    result += "\nfunction %s__init_fields__() {" % clazz + indent("\n".join(fields)) + "}\n"
    result += "%s.prototype.__init_fields__ = %s__init_fields__;\n" % (clazz, clazz)

    result += "\n".join(methods)

    return result

def field(doc, type, name, value):
    return "%sthis.%s = %s;" % (doc, name, value or "null")

def field_init():
    return "this.__init_fields__();"

def default_constructor(clazz):
    return "function %s() {\n    this.__init_fields__();\n}\nexports.%s = %s;\n" % \
        (clazz, clazz, clazz)

def constructor(doc, name, parameters, body):
    return "\n%sfunction %s(%s)%s\nexports.%s = %s;\n" % \
        (doc, name, ", ".join(parameters), body, name, name)

def method(doc, clazz, type, name, parameters, body):
    params = ", ".join(parameters)
    full_name = "%s_%s" % (clazz, name)
    trailer = "%s.prototype.%s = %s;" % (clazz, name, full_name)
    return "\n%sfunction %s(%s)%s\n" % (doc, full_name, params, body) + trailer

def abstract_method(doc, clazz, type, name, parameters):
    params = ", ".join(parameters)
    full_name = "%s_%s" % (clazz, name)
    trailer = "%s.prototype.%s = %s;" % (clazz, name, full_name)
    return "\n%sfunction %s(%s) { /* abstract */ }\n" % (doc, full_name, params) + trailer

## Interface definition

def interface(doc, iface, parameters, bases, methods):
    return clazz(doc, False, iface, parameters, None, [], [], [default_constructor(iface)], methods)

def interface_method(doc, iface, type, name, parameters, body):
    params = ", ".join(parameters)
    full_name = "%s_%s" % (iface, name)
    trailer = "%s.prototype.%s = %s;" % (iface, name, full_name)
    if body is None:
        body = " { /* interface */ }"

    return "\n%sfunction %s(%s)%s\n" % (doc, full_name, params, body) + trailer

## Function definition

def function(doc, type, name, parameters, body):
    trailer = "exports.%s = %s;" % (name, name)
    return "\n%sfunction %s(%s)%s\n" % (doc, name, ", ".join(parameters), body) + trailer

## Parameters for methods and functions

def param(type, name, value):
    if value is None:
        return "%s" % name
    else:
        return "%s = %s" % (name, value)

## Blocks

def block(statements):
    return " {%s}" % indent("\n".join(statements))

## Statements

def local(type, name, value):
    return "var %s = %s;" % (name, value or "null")

def expr_stmt(e):
    return "%s;" % e

def assign(lhs, rhs):
    return "%s = %s;" % (lhs, rhs)

def if_(pred, cons, alt):
    result = "if (%s)%s" % (pred, cons)
    if alt:
        result += " else%s" % alt
    return result

def while_(cond, body):
    return "while (%s)%s" % (cond, body)

def break_():
    return "break;"

def continue_():
    return "continue;"

def return_(expr):
    if expr:
        return "return %s;" % expr
    else:
        return "return;"

## Expressions

def class_ref(v):
    return v

def method_ref(v):
    return "this.%s" % v

def field_ref(v):
    return "this.%s" % v

def local_ref(v):
    return v

def invoke_function(path, name, args):
    return "%s(%s)" % (".".join(path + [name]), ", ".join(args))

def construct(clazz, args):
    return "new %s(%s)" % (clazz, ", ".join(args))

def invoke_super(clazz, base, args):
    return "%s.super_.call(%s)" % (clazz, ", ".join(["this"] + args))

def invoke_method(expr, method, args):
    return "(%s).%s(%s)" % (expr, method, ", ".join(args))

def invoke_method_implicit(method, args):
    return "this.%s(%s)" % (method, ", ".join(args))

def invoke_super_method(clazz, base, method, args):
    return "this.constructor.super_.prototype.%s.call(%s)" % (method, ", ".join(["this"] + args))

def get_field(expr, field):
    return "(%s).%s" % (expr, field)

def cast(type, expr):
    return expr

## Literals

def null():
    return "null"

def bool_(b):
    return b.text

def number(n):
    return n.text

def string(s):
    result = s.text[0]
    idx = 1
    while idx < len(s.text) - 1:
        c = s.text[idx]
        next = s.text[idx + 1]
        if c == "\\" and next == "x":
            result += "\\u00"
            idx += 1
        else:
            result += c
        idx += 1
    result += s.text[-1]
    return result

def list(elements):
    return "[%s]" % ", ".join(elements)

def map(entries):
    return "new Map([%s])" % (", ".join(["[%s, %s]" % e for e in entries]))
