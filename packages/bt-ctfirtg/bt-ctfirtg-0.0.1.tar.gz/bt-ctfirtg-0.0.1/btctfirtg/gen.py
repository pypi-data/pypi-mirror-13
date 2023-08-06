# The MIT License (MIT)
#
# Copyright (c) 2015 Philippe Proulx <pproulx@efficios.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from btctfirtg import metadata
import btctfirtg.codegen
import collections
import btctfirtg


class _TypeStackElement:
    def __init__(self, t, name):
        self._type = t
        self._name = name

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name


class _TypeStack:
    def __init__(self):
        self._stack = []

    def push(self, t, name):
        self._stack.append(_TypeStackElement(t, name))

    def pop(self):
        self._stack.pop()

    def peek(self):
        return self._stack[-1]

    def clear(self):
        del self._stack[:]

    def is_empty(self):
        return len(self._stack) > 0

    @property
    def elements(self):
        return self._stack

    def __len__(self):
        return len(self._stack)


_compound_types = [
    metadata.Struct,
    metadata.Array,
    metadata.Variant,
]


_root_name = 'root'
_array_elem_name = 'elem'
_enum_value_type = 'int'


def _is_compound_type(t):
    return type(t) in _compound_types


def _get_var_name(name, stack):
    names = [elem.name for elem in stack.elements]

    if name is not None:
        names.append(name)

    return '_'.join(names)


class _SimpleGeneratorVisitor:
    def __init__(self):
        self._stack = _TypeStack()

    def _gen_line(self, t, name):
        var_name = _get_var_name(name, self._stack)
        line = self._TMPL.format(var_name)
        self._cg.add_line(line)

    def _gen(self, t, name):
        self._gen_line(t, name)

        if _is_compound_type(t):
            self._stack.push(t, name)

        if type(t) is metadata.Struct:
            for field_name, field_type in t.fields.items():
                self._gen(field_type, field_name)
        elif type(t) is metadata.Array:
            self._gen(t.element_type, _array_elem_name)
        elif type(t) is metadata.Variant:
            for type_name, type_type in t.types.items():
                self._gen(type_type, type_name)
        elif type(t) is metadata.Enum:
            self._stack.push(t, name)
            self._gen(t.value_type, _enum_value_type)
            self._stack.pop()

        if _is_compound_type(t):
            self._stack.pop()

    def generate(self, root_type, cg):
        self._stack.clear()
        self._cg = cg
        self._gen(root_type, _root_name)


class _DeclGeneratorVisitor(_SimpleGeneratorVisitor):
    _TMPL = 'struct bt_ctf_field_type *{} = NULL;'


class _RefPutGeneratorVisitor(_SimpleGeneratorVisitor):
    _TMPL = 'bt_ctf_field_type_put({});'

    def __init__(self, no_put_root):
        super().__init__()
        self._no_put_root = no_put_root

    def generate(self, root_type, cg):
        self._stack.clear()
        self._root_type = root_type
        self._cg = cg
        self._gen(root_type, _root_name)

    def _gen_line(self, t, name):
        if self._no_put_root and t is self._root_type:
            return

        super()._gen_line(t, name)


def _bool_to_int(b):
    return '1' if b else '0'


def _encoding_to_enum(encoding):
    enums = {
        metadata.Encoding.NONE: 'CTF_STRING_NONE',
        metadata.Encoding.ASCII: 'CTF_STRING_ASCII',
        metadata.Encoding.UTF8: 'CTF_STRING_UTF8',
    }

    return enums[encoding]


def _bo_to_enum(bo):
    enums = {
        metadata.ByteOrder.LE: 'BT_CTF_BYTE_ORDER_LITTLE_ENDIAN',
        metadata.ByteOrder.BE: 'BT_CTF_BYTE_ORDER_BIG_ENDIAN',
    }

    return enums[bo]


class _CreationGeneratorVisitor:
    def __init__(self):
        self._stack = _TypeStack()
        self._type_to_gen_creation_func = {
            metadata.Integer: self._gen_create_int,
            metadata.FloatingPoint: self._gen_create_float,
            metadata.Enum: None,
            metadata.String: self._gen_create_string,
            metadata.Struct: self._gen_create_struct,
            metadata.Array: None,
            metadata.Variant: self._gen_create_variant,
        }

    def _gen_assert(self, var_name):
        if self._with_asserts:
            self._cg.add_line('assert({});'.format(var_name))

    def _gen_ret_call(self, line):
        if self._with_asserts:
            line = 'ret = ' + line

        self._cg.add_line(line)

        if self._with_asserts:
            self._cg.add_line('assert(ret == 0);')

    def _gen_set_byte_order(self, t, var_name):
        tmpl = 'bt_ctf_field_type_set_byte_order({}, {});'
        line = tmpl.format(var_name, _bo_to_enum(t.byte_order))
        self._gen_ret_call(line)

    def _gen_set_alignment(self, t, var_name):
        tmpl = 'bt_ctf_field_type_set_alignment({}, {});'
        line = tmpl.format(var_name, t.align)
        self._gen_ret_call(line)

    def _gen_create_int(self, t, name, var_name):
        # creation (size)
        tmpl = '{} = bt_ctf_field_type_integer_create({});'
        line = tmpl.format(var_name, t.size)
        self._cg.add_line(line)
        self._gen_assert(var_name)

        # signed
        tmpl = 'bt_ctf_field_type_integer_set_signed({}, {});'
        line = tmpl.format(var_name, _bool_to_int(t.signed))
        self._gen_ret_call(line)

        # base
        tmpl = 'bt_ctf_field_type_integer_set_base({}, {});'
        line = tmpl.format(var_name, t.base)
        self._gen_ret_call(line)

        # encoding
        tmpl = 'bt_ctf_field_type_integer_set_encoding({}, {});'
        line = tmpl.format(var_name, _encoding_to_enum(t.encoding))
        self._gen_ret_call(line)

        # byte order
        self._gen_set_byte_order(t, var_name)

        # alignment
        self._gen_set_alignment(t, var_name)

    def _gen_create_float(self, t, name, var_name):
        # creation
        tmpl = '{} = bt_ctf_field_type_floating_point_create();'
        line = tmpl.format(var_name)
        self._cg.add_line(line)
        self._gen_assert(var_name)

        # exponent digits
        tmpl = 'bt_ctf_field_type_floating_point_set_exponent_digits({}, {});'
        line = tmpl.format(var_name, t.exp_size)
        self._gen_ret_call(line)

        # mantissa digits
        tmpl = 'bt_ctf_field_type_floating_point_set_mantissa_digits({}, {});'
        line = tmpl.format(var_name, t.mant_size)
        self._gen_ret_call(line)

        # byte order
        self._gen_set_byte_order(t, var_name)

        # alignment
        self._gen_set_alignment(t, var_name)

    def _gen_create_enum(self, t, name, var_name):
        # creation (value type's variable name)
        int_var_name = _get_var_name(_enum_value_type, self._stack)
        tmpl = '{} = bt_ctf_field_type_enumeration_create({});'
        line = tmpl.format(var_name, int_var_name)
        self._cg.add_line(line)
        self._gen_assert(var_name)

        # mappings
        for label, rg in t.members.items():
            tmpl = 'bt_ctf_field_type_enumeration_add_mapping({}, "{}", {}, {});'
            line = tmpl.format(var_name, label, rg[0], rg[1])
            self._gen_ret_call(line)

    def _gen_create_string(self, t, name, var_name):
        # creation
        tmpl = '{} = bt_ctf_field_type_string_create();'
        line = tmpl.format(var_name)
        self._cg.add_line(line)
        self._gen_assert(var_name)

        # encoding
        tmpl = 'bt_ctf_field_type_string_set_encoding({}, {});'
        line = tmpl.format(var_name, _encoding_to_enum(t.encoding))
        self._gen_ret_call(line)

    def _gen_create_struct(self, t, name, var_name):
        # creation
        tmpl = '{} = bt_ctf_field_type_structure_create();'
        line = tmpl.format(var_name)
        self._cg.add_line(line)
        self._gen_assert(var_name)

        # alignment
        self._gen_set_alignment(t, var_name)

    def _gen_create_array(self, t, name, var_name):
        # creation
        elem_var_name = _get_var_name(_array_elem_name, self._stack)

        if type(t.length) is int:
            tmpl = '{} = bt_ctf_field_type_array_create({}, {});'
            line = tmpl.format(var_name, elem_var_name, t.length)
        else:
            tmpl = '{} = bt_ctf_field_type_sequence_create({}, "{}");'
            line = tmpl.format(var_name, elem_var_name, t.length)

        self._cg.add_line(line)
        self._gen_assert(var_name)

    def _gen_create_variant(self, t, name, var_name):
        # creation
        tmpl = '{} = bt_ctf_field_type_variant_create(NULL, "{}");'
        line = tmpl.format(var_name, t.tag)
        self._cg.add_line(line)
        self._gen_assert(var_name)

    def _gen_creation(self, t, name):
        var_name = _get_var_name(name, self._stack)
        func = self._type_to_gen_creation_func[type(t)]

        if func is not None:
            func(t, name, var_name)

    def _gen(self, t, name):
        self._gen_creation(t, name)

        if _is_compound_type(t):
            self._stack.push(t, name)

        if type(t) is metadata.Struct:
            cur_var_name = _get_var_name(None, self._stack)

            for field_name, field_type in t.fields.items():
                self._gen(field_type, field_name)
                tmpl = 'bt_ctf_field_type_structure_add_field({}, {}, "{}");'
                line = tmpl.format(cur_var_name,
                                   cur_var_name + '_' + field_name,
                                   field_name)
                self._gen_ret_call(line)
        elif type(t) is metadata.Array:
            # create element type
            self._gen(t.element_type, _array_elem_name)

            # create array now
            cur_var_name = _get_var_name(None, self._stack)
            self._gen_create_array(t, name, cur_var_name)
        elif type(t) is metadata.Variant:
            cur_var_name = _get_var_name(None, self._stack)

            for type_name, type_type in t.types.items():
                self._gen(type_type, type_name)
                tmpl = 'bt_ctf_field_type_variant_add_field({}, {}, "{}");'
                line = tmpl.format(cur_var_name,
                                   cur_var_name + '_' + type_name,
                                   type_name)
                self._gen_ret_call(line)
        elif type(t) is metadata.Enum:
            # create value type
            self._stack.push(t, name)
            self._gen(t.value_type, _enum_value_type)

            # create enumeration now
            cur_var_name = _get_var_name(None, self._stack)
            self._gen_create_enum(t, name, cur_var_name)
            self._stack.pop()

        if _is_compound_type(t):
            self._stack.pop()

    def generate(self, root_type, cg, with_asserts):
        self._with_asserts = with_asserts
        self._stack.clear()
        self._cg = cg

        if with_asserts:
            self._cg.add_line('int ret;')

        self._gen(root_type, _root_name)


class CCodeGenerator:
    def __init__(self, indent=0):
        self._cg = btctfirtg.codegen.CodeGenerator('\t')

        for i in range(indent):
            self._cg.indent()

    def generate_declarations(self, t):
        self._cg.clear()
        decl_generator = _DeclGeneratorVisitor()
        decl_generator.generate(t, self._cg)

        return self._cg.code

    def generate_creations(self, t, with_asserts=True):
        self._cg.clear()
        creation_generator = _CreationGeneratorVisitor()
        creation_generator.generate(t, self._cg, with_asserts)

        return self._cg.code

    def generate_put_references(self, t, no_put_root):
        self._cg.clear()
        creation_generator = _RefPutGeneratorVisitor(no_put_root)
        creation_generator.generate(t, self._cg)

        return self._cg.code
