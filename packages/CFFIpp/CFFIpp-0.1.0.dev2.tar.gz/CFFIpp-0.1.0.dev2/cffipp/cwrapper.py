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


class CWrapper:

    def __init__(self, ffi):
        self._ffi = ffi
        self._class_sources = []
        self._classes = []

    def wrap_class(self, clazz):
        self._classes.append(clazz)
        # Wrapper struct
        declaration = "typedef struct _" + clazz.name + " " + clazz.name + ";"
        self._ffi.cdef(declaration)

        if clazz.constructor is not None:
            f = clazz.constructor
            declaration = clazz.name + " * construct_" + clazz.name
            # Arguments
            declaration += "("
            declaration += ", ".join(f.parameters)
            declaration += ");"
            self._ffi.cdef(declaration)

        declaration = "void destruct_" + clazz.name
        declaration += "({} *);".format(clazz.name)
        self._ffi.cdef(declaration)

        for f in clazz.methods:
            if f.accessor != "public":
                continue
            declaration = f.returnType + " " + \
                self.generate_function_name(clazz, f)
            # Arguments
            declaration += "("
            p = [clazz.name + " *"]
            p.extend(f.parameters)
            declaration += ", ".join(p)
            declaration += ");"
            self._ffi.cdef(declaration)

    def generate_function_name(self, c, f):
        return c.name + '_' + f.name

    def generate_source(self):
        for clazz in self._classes:
            sources = []
            if clazz.constructor is not None:
                f = clazz.constructor
                if f.accessor != "public":
                    continue
                source = clazz.name + " * construct_" + clazz.name
                formal_args = [(t, "param{}".format(i))
                               for i, t in enumerate(f.parameters)]
                source += "("
                source += ", ".join(["{} {}".format(x, y)
                                     for x, y in formal_args])
                source += ") {\n"

                actual_args = [y for x, y in formal_args]
                source += "    return new " + clazz.name + \
                    "({});\n".format(", ".join(actual_args))
                source += "}"
                sources.append(source)

            # Generate destructor
            source = "void destruct_" + clazz.name
            source += "(" + clazz.name + " *obj) {\n"

            source += "    delete obj;\n"
            source += "}"
            sources.append(source)

            for f in clazz.methods:
                if f.accessor != "public":
                    continue
                source = " ".join(
                    [f.returnType, self.generate_function_name(clazz, f)])
                # Arguments
                source += "("
                p = [clazz.name + " *obj"]
                p.extend(["{} param{}".format(p, i)
                          for i, p in enumerate(f.parameters)])
                source += ", ".join(p)
                source += ") {\n"
                if f.returnType == "void":
                    source += "    obj->" + f.name + "("
                else:
                    source += "    return obj->" + f.name + "("
                source += ", ".join(["param{}".format(i)
                                     for i in range(len(f.parameters))])
                source += ");\n"
                source += "}"
                sources.append(source)
            yield "\n\n".join(sources)
