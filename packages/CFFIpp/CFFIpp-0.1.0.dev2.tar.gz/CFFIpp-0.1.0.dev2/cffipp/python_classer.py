# Copyright 2016 -  Ruben De Smet
#
# This file is part of CFFIpp.
#
# CFFIpp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CFFIpp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CFFIpp.  If not, see <http://www.gnu.org/licenses/>.

import sys
import string

# Python code generator backend
# Python 3 adaption by Ruben De Smet, 2016
#
# Fredrik Lundh, march 1998
#
# fredrik@pythonware.com
# http://www.pythonware.com
#


class CodeGeneratorBackend:

    def begin(self, tab=" "*4):
        self.code = []
        self.tab = tab
        self.level = 0

    def end(self):
        return "".join(self.code)

    def write(self, string):
        self.code.append(self.tab * self.level + string + "\n")

    def indent(self):
        self.level = self.level + 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError("internal error in code generator")
        self.level = self.level - 1


class PythonClasser:

    def __init__(self):
        self._classes = []

    def wrap_class(self, clazz):
        self._classes.append(clazz)

    def generate_source(self, module_name):
        cog = CodeGeneratorBackend()
        cog.begin()
        cog.write("from _{} import ffi, lib".format(module_name))
        cog.write("")
        for clazz in self._classes:
            cog.write("class " + clazz.name + "{}:".format(
                "({})".format(clazz.python_parent) if clazz.python_parent else ""))
            cog.indent()

            cog.write("def __del__(self):")
            cog.indent()
            cog.write("if self.self_constructed:")
            cog.indent()
            cog.write("lib.destruct_{}(self.obj)".format(clazz.name))
            cog.dedent()
            cog.dedent()

            if clazz.constructor is not None:
                if clazz.constructor.accessor != "public":
                    continue
                cog.write("def __init__(self, *args):")
                cog.indent()
                cog.write("self.obj = lib.construct_{}(*args)".format(clazz.name))
                cog.write("self.self_constructed = True")
                cog.dedent()
            else:
                cog.write("def __init__(self):")
                cog.indent()
                cog.write(
                    "raise RuntimeError(\"Class `{}' not constructible\")".format(clazz.name))
                cog.dedent()

            for method in clazz.methods:
                if method.accessor != "public":
                    continue
                cog.write("def {}(self, *args):".format(method.name))
                cog.indent()
                ret = ""
                if method.returnType != "void":
                    ret = "return "
                cog.write("{}lib.{}(self.obj, *args)".format(ret,
                                                             clazz.name + "_" + method.name))
                cog.dedent()
            cog.dedent()

        return cog.end()
