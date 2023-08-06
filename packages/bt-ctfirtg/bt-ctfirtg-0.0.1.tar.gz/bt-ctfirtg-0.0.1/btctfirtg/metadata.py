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

import enum
import collections


@enum.unique
class ByteOrder(enum.Enum):
    LE = 0
    BE = 1


@enum.unique
class Encoding(enum.Enum):
    NONE = 0
    UTF8 = 1
    ASCII = 2


class Type:
    @property
    def align(self):
        raise NotImplementedError()

    @property
    def size(self):
        raise NotImplementedError()

    @size.setter
    def size(self, value):
        self._size = value


class PropertyMapping:
    def __init__(self, object, prop):
        self._object = object
        self._prop = prop

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self, value):
        self._object = value

    @property
    def prop(self):
        return self.prop

    @prop.setter
    def prop(self, value):
        self.prop = value


class Integer(Type):
    def __init__(self):
        self._size = None
        self._align = None
        self._signed = False
        self._byte_order = None
        self._base = 10
        self._encoding = Encoding.NONE
        self._property_mappings = []

    @property
    def signed(self):
        return self._signed

    @signed.setter
    def signed(self, value):
        self._signed = value

    @property
    def byte_order(self):
        return self._byte_order

    @byte_order.setter
    def byte_order(self, value):
        self._byte_order = value

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = value

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    def align(self):
        if self._align is None:
            if self._size is None:
                return None
            else:
                if self._size % 8 == 0:
                    return 8
                else:
                    return 1
        else:
            return self._align

    @align.setter
    def align(self, value):
        self._align = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def property_mappings(self):
        return self._property_mappings


class FloatingPoint(Type):
    def __init__(self):
        self._exp_size = None
        self._mant_size = None
        self._align = 8
        self._byte_order = None

    @property
    def exp_size(self):
        return self._exp_size

    @exp_size.setter
    def exp_size(self, value):
        self._exp_size = value

    @property
    def mant_size(self):
        return self._mant_size

    @mant_size.setter
    def mant_size(self, value):
        self._mant_size = value

    @property
    def size(self):
        return self._exp_size + self._mant_size

    @property
    def byte_order(self):
        return self._byte_order

    @byte_order.setter
    def byte_order(self, value):
        self._byte_order = value

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, value):
        self._align = value


class Enum(Type):
    def __init__(self):
        self._value_type = None
        self._members = collections.OrderedDict()

    @property
    def align(self):
        return self._value_type.align

    @property
    def size(self):
        return self._value_type.size

    @property
    def value_type(self):
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        self._value_type = value

    @property
    def members(self):
        return self._members

    def value_of(self, label):
        return self._members[label]

    def label_of(self, value):
        for label, vrange in self._members.items():
            if value >= vrange[0] and value <= vrange[1]:
                return label

    def __getitem__(self, key):
        if type(key) is str:
            return self.value_of(key)
        elif type(key) is int:
            return self.label_of(key)

        raise TypeError('wrong subscript type')


class String(Type):
    def __init__(self):
        self._encoding = Encoding.UTF8

    @property
    def size(self):
        return None

    @property
    def align(self):
        return 8

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value


class Array(Type):
    def __init__(self):
        self._element_type = None
        self._length = None

    @property
    def align(self):
        return self._element_type.align

    @property
    def element_type(self):
        return self._element_type

    @element_type.setter
    def element_type(self, value):
        self._element_type = value

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def is_static(self):
        return type(self._length) is int

    @property
    def size(self):
        if self.length == 0:
            return 0

        element_sz = self.element_type.size

        if element_sz is None:
            return None

        # TODO: compute static size here
        return None


class Struct(Type):
    def __init__(self):
        self._min_align = 1
        self._fields = collections.OrderedDict()

    @property
    def min_align(self):
        return self._min_align

    @min_align.setter
    def min_align(self, value):
        self._min_align = value

    @property
    def align(self):
        fields_max = max([f.align for f in self.fields.values()] + [1])

        return max(fields_max, self._min_align)

    @property
    def size(self):
        # TODO: compute static size here (if available)
        return None

    @property
    def fields(self):
        return self._fields

    def __getitem__(self, key):
        return self.fields[key]


class Variant(Type):
    def __init__(self):
        self._tag = None
        self._types = collections.OrderedDict()

    @property
    def align(self):
        return 1

    @property
    def size(self):
        if len(self.members) == 1:
            return list(self.members.values())[0].size

        return None

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def types(self):
        return self._types

    def __getitem__(self, key):
        return self.types[key]
