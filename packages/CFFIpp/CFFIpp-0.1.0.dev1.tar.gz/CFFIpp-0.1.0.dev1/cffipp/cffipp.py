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

import clang
import clang.cindex
import tempfile
from cffi import FFI
from .python_classer import PythonClasser
from .cwrapper import CWrapper

from ctypes.util import find_library
clang.cindex.Config.set_library_file(find_library('clang'))


class FFIpp:

    def __init__(self):
        self._ffi = FFI()
        self._index = clang.cindex.Index.create()
        self.classes = {}
        self.sources = []
        self.pyclasser = PythonClasser()
        self.cwrapper = CWrapper(self._ffi)

    def set_source(self, name, code, *args, **kwargs):
        codes = [code]
        codes.extend(self.cwrapper.generate_source())
        code = "\n\n".join(codes)
        self._ffi.set_source("_" + name, code,
                             source_extension=".cpp",
                             extra_compile_args=["-std=c++14"], *args, **kwargs)

        self.sources.append(name)

    def compile(self):
        self._ffi.compile()
        for name in self.sources:
            f = open(name + ".py", "w+")
            f.write(self.pyclasser.generate_source(name))
            f.close()

    def cdef(self, header_source):
        # Write out the .hpp source for clang
        with tempfile.NamedTemporaryFile(suffix='.hpp') as f:
            f.write(header_source.encode('utf-8'))
            f.flush()
            file_name = f.name
            tu = self._index.parse(file_name, ['-x', 'c++', '-std=c++14'])

        classes = []

        def parse_node(node):
            if node.kind == clang.cindex.CursorKind.CLASS_DECL:
                classes.append(Class(node))
                return True
            return False

        def recurse_nodes(node):
            if not parse_node(node):
                for n in node.get_children():
                    if n.location.file.name != file_name:
                        return
                    recurse_nodes(n)

        recurse_nodes(tu.cursor)

        for c in classes:
            self.generate_class(c)

    def generate_class(self, clazz):
        self.classes[clazz.name] = clazz
        self.pyclasser.wrap_class(clazz)
        self.cwrapper.wrap_class(clazz)

    def has_class(self, name):
        return name in self.classes

    def get_class(self, name):
        return self.classes[name]


class Class:

    def __init__(self, cursor):
        self.name = cursor.spelling
        self.methods = []
        self.constructor = None
        self.python_parent = None

        for c in cursor.get_children():
            if c.kind == clang.cindex.CursorKind.CXX_METHOD:
                self.methods.append(Method(c))
            elif c.kind == clang.cindex.CursorKind.CONSTRUCTOR:
                self.parse_constructor(c)

    def parse_constructor(self, cursor):
        self.constructor = Method(cursor)

    def has_method(self, name):
        return name in [m.name for m in self.methods]

    def has_public_method(self, name):
        return name in [m.name for m in self.methods if m.accessor == "public"]

    def set_python_parent(self, python_parent):
        self.python_parent = python_parent


class Method:

    def __init__(self, cursor):
        self.name = cursor.spelling
        self.returnType = cursor.result_type.spelling
        self.parameters = []
        self.accessor = cursor.access_specifier.name.lower()

        for arg in cursor.get_arguments():
            self.parameters.append(arg.type.spelling)
