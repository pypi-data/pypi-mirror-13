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
import collections
import btctfirtg
import enum
import yaml
import re


class ConfigError(RuntimeError):
    def __init__(self, msg, prev=None):
        super().__init__(msg)
        self._prev = prev

    @property
    def prev(self):
        return self._prev


class Config:
    def __init__(self, root_type):
        self._root_type = root_type
        self._validate()

    def _validate(self):
        validator = _MetadataTypesHistologyValidator()
        validator.validate(self._root_type)

    @property
    def root_type(self):
        return self._root_type

    @root_type.setter
    def root_type(self, value):
        self._root_type = value


class _MetadataTypesHistologyValidator:
    def __init__(self):
        self._type_to_validate_type_histology_func = {
            metadata.Integer: self._validate_integer_histology,
            metadata.FloatingPoint: self._validate_float_histology,
            metadata.Enum: self._validate_enum_histology,
            metadata.String: self._validate_string_histology,
            metadata.Struct: self._validate_struct_histology,
            metadata.Array: self._validate_array_histology,
            metadata.Variant: self._validate_variant_histology,
        }

    def _validate_integer_histology(self, t):
        # size is set
        if t.size is None:
            raise ConfigError('missing integer type\'s size')

    def _validate_float_histology(self, t):
        # exponent digits is set
        if t.exp_size is None:
            raise ConfigError('missing floating point number type\'s exponent size')

        # mantissa digits is set
        if t.mant_size is None:
            raise ConfigError('missing floating point number type\'s mantissa size')

        # exponent and mantissa sum is a multiple of 8
        if (t.exp_size + t.mant_size) % 8 != 0:
            raise ConfigError('floating point number type\'s mantissa and exponent sizes sum must be a multiple of 8')

    def _validate_enum_histology(self, t):
        # integer type is set
        if t.value_type is None:
            raise ConfigError('missing enumeration type\'s integer type')

        # there's at least one member
        if not t.members:
            raise ConfigError('enumeration type needs at least one member')

        # no overlapping values
        ranges = []

        for label, value in t.members.items():
            for rg in ranges:
                if value[0] <= rg[1] and rg[0] <= value[1]:
                    raise ConfigError('enumeration type\'s member "{}" overlaps another member'.format(label))

            ranges.append(value)

    def _validate_string_histology(self, t):
        # always valid
        pass

    def _validate_struct_histology(self, t):
        # all fields are valid
        for field_name, field_type in t.fields.items():
            try:
                self._validate_type_histology(field_type)
            except Exception as e:
                raise ConfigError('invalid structure type\'s field "{}"'.format(field_name), e)

    def _validate_array_histology(self, t):
        # length is set
        if t.length is None:
            raise ConfigError('missing array type\'s length')

        # element type is set
        if t.element_type is None:
            raise ConfigError('missing array type\'s element type')

        # element type is valid
        try:
            self._validate_type_histology(t.element_type)
        except Exception as e:
            raise ConfigError('invalid array type\'s element type', e)

    def _validate_variant_histology(self, t):
        # tag is set
        if t.tag is None:
            raise ConfigError('missing variant type\'s tag')

        # there's at least one type
        if not t.types:
            raise ConfigError('variant type needs at least one type')

        # all types are valid
        for type_name, type_t in t.types.items():
            try:
                self._validate_type_histology(type_t)
            except Exception as e:
                raise ConfigError('invalid variant type\'s type "{}"'.format(type_name), e)

    def _validate_type_histology(self, t):
        if t is None:
            return

        self._type_to_validate_type_histology_func[type(t)](t)

    def validate(self, root_type):
        self._validate_type_histology(root_type)


def _is_assoc_array_prop(node):
    return isinstance(node, dict)


def _is_array_prop(node):
    return isinstance(node, list)


def _is_int_prop(node):
    return type(node) is int


def _is_str_prop(node):
    return type(node) is str


def _is_bool_prop(node):
    return type(node) is bool


def _is_valid_alignment(align):
    return ((align & (align - 1)) == 0) and align > 0


def _byte_order_str_to_bo(bo_str):
    bo_str = bo_str.lower()

    if bo_str == 'le':
        return metadata.ByteOrder.LE
    elif bo_str == 'be':
        return metadata.ByteOrder.BE


def _encoding_str_to_encoding(encoding_str):
    encoding_str = encoding_str.lower()

    if encoding_str == 'utf-8' or encoding_str == 'utf8':
        return metadata.Encoding.UTF8
    elif encoding_str == 'ascii':
        return metadata.Encoding.ASCII
    elif encoding_str == 'none':
        return metadata.Encoding.NONE


_re_iden = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
_ctf_keywords = set([
    'align',
    'callsite',
    'clock',
    'enum',
    'env',
    'event',
    'floating_point',
    'integer',
    'stream',
    'string',
    'struct',
    'trace',
    'typealias',
    'typedef',
    'variant',
])


def is_valid_identifier(iden):
    if not _re_iden.match(iden):
        return False

    if _re_iden in _ctf_keywords:
        return False

    return True


def _get_first_unknown_prop(node, known_props):
    for prop_name in node:
        if prop_name in known_props:
            continue

        return prop_name


def _get_first_unknown_type_prop(type_node, known_props):
    kp = known_props + ['inherit', 'class']

    return _get_first_unknown_prop(type_node, kp)


class _YamlConfigParser:
    def __init__(self):
        self._class_name_to_create_type_func = {
            'int': self._create_integer,
            'integer': self._create_integer,
            'flt': self._create_float,
            'float': self._create_float,
            'floating-point': self._create_float,
            'enum': self._create_enum,
            'enumeration': self._create_enum,
            'str': self._create_string,
            'string': self._create_string,
            'struct': self._create_struct,
            'structure': self._create_struct,
            'array': self._create_array,
            'var': self._create_variant,
            'variant': self._create_variant,
        }
        self._type_to_create_type_func = {
            metadata.Integer: self._create_integer,
            metadata.FloatingPoint: self._create_float,
            metadata.Enum: self._create_enum,
            metadata.String: self._create_string,
            metadata.Struct: self._create_struct,
            metadata.Array: self._create_array,
            metadata.Variant: self._create_variant,
        }
        self._bo = metadata.ByteOrder.LE

    def _set_int_clock_prop_mapping(self, int_obj, prop_mapping_node):
        unk_prop = _get_first_unknown_prop(prop_mapping_node, ['type', 'name', 'property'])

        if unk_prop:
            raise ConfigError('unknown property in integer type object\'s clock property mapping: "{}"'.format(unk_prop))

        if 'name' not in prop_mapping_node:
            raise ConfigError('missing "name" property in integer type object\'s clock property mapping')

        if 'property' not in prop_mapping_node:
            raise ConfigError('missing "property" property in integer type object\'s clock property mapping')

        clock_name = prop_mapping_node['name']
        prop = prop_mapping_node['property']

        if not _is_str_prop(clock_name):
            raise ConfigError('"name" property of integer type object\'s clock property mapping must be a string')

        if not _is_str_prop(prop):
            raise ConfigError('"property" property of integer type object\'s clock property mapping must be a string')

        if clock_name not in self._clocks:
            raise ConfigError('invalid clock name "{}" in integer type object\'s clock property mapping'.format(clock_name))

        if prop != 'value':
            raise ConfigError('invalid "property" property in integer type object\'s clock property mapping: "{}"'.format(prop))

        mapped_clock = self._clocks[clock_name]
        int_obj.property_mappings.append(metadata.PropertyMapping(mapped_clock, prop))

    def _create_integer(self, obj, node):
        if obj is None:
            # create integer object
            obj = metadata.Integer()

        unk_prop = _get_first_unknown_type_prop(node, [
            'size',
            'align',
            'signed',
            'byte-order',
            'base',
            'encoding',
            'property-mappings',
        ])

        if unk_prop:
            raise ConfigError('unknown integer type object property: "{}"'.format(unk_prop))

        # size
        if 'size' in node:
            size = node['size']

            if not _is_int_prop(size):
                raise ConfigError('"size" property of integer type object must be an integer')

            if size < 1:
                raise ConfigError('invalid integer size: {}'.format(size))

            obj.size = size

        # align
        if 'align' in node:
            align = node['align']

            if not _is_int_prop(align):
                raise ConfigError('"align" property of integer type object must be an integer')

            if not _is_valid_alignment(align):
                raise ConfigError('invalid alignment: {}'.format(align))

            obj.align = align

        # signed
        if 'signed' in node:
            signed = node['signed']

            if not _is_bool_prop(signed):
                raise ConfigError('"signed" property of integer type object must be a boolean')

            obj.signed = signed

        # byte order
        if 'byte-order' in node:
            byte_order = node['byte-order']

            if not _is_str_prop(byte_order):
                raise ConfigError('"byte-order" property of integer type object must be a string ("le" or "be")')

            byte_order = _byte_order_str_to_bo(byte_order)

            if byte_order is None:
                raise ConfigError('invalid "byte-order" property in integer type object')
        else:
            byte_order = self._bo

        obj.byte_order = byte_order

        # base
        if 'base' in node:
            base = node['base']

            if not _is_str_prop(base):
                raise ConfigError('"base" property of integer type object must be a string ("bin", "oct", "dec", or "hex")')

            if base == 'bin':
                base = 2
            elif base == 'oct':
                base = 8
            elif base == 'dec':
                base = 10
            elif base == 'hex':
                base = 16

            obj.base = base

        # encoding
        if 'encoding' in node:
            encoding = node['encoding']

            if not _is_str_prop(encoding):
                raise ConfigError('"encoding" property of integer type object must be a string ("none", "ascii", or "utf-8")')

            encoding = _encoding_str_to_encoding(encoding)

            if encoding is None:
                raise ConfigError('invalid "encoding" property in integer type object')

            obj.encoding = encoding

        # property mappings
        if 'property-mappings' in node:
            prop_mappings = node['property-mappings']

            if not _is_array_prop(prop_mappings):
                raise ConfigError('"property-mappings" property of integer type object must be an array')

            if len(prop_mappings) > 1:
                raise ConfigError('length of "property-mappings" array in integer type object must be 1')

            del obj.property_mappings[:]

            for index, prop_mapping in enumerate(prop_mappings):
                if not _is_assoc_array_prop(prop_mapping):
                    raise ConfigError('elements of "property-mappings" property of integer type object must be associative arrays')

                if 'type' not in prop_mapping:
                    raise ConfigError('missing "type" property in integer type object\'s "property-mappings" array\'s element #{}'.format(index))

                prop_type = prop_mapping['type']

                if not _is_str_prop(prop_type):
                    raise ConfigError('"type" property of integer type object\'s "property-mappings" array\'s element #{} must be a string'.format(index))

                if prop_type == 'clock':
                    self._set_int_clock_prop_mapping(obj, prop_mapping)
                else:
                    raise ConfigError('unknown property mapping type "{}" in integer type object\'s "property-mappings" array\'s element #{}'.format(prop_type, index))

        return obj

    def _create_float(self, obj, node):
        if obj is None:
            # create floating point number object
            obj = metadata.FloatingPoint()

        unk_prop = _get_first_unknown_type_prop(node, [
            'size',
            'align',
            'byte-order',
        ])

        if unk_prop:
            raise ConfigError('unknown floating point number type object property: "{}"'.format(unk_prop))

        # size
        if 'size' in node:
            size = node['size']

            if not _is_assoc_array_prop(size):
                raise ConfigError('"size" property of floating point number type object must be an associative array')

            unk_prop = _get_first_unknown_prop(node, ['exp', 'mant'])

            if 'exp' in size:
                exp = size['exp']

                if not _is_int_prop(exp):
                    raise ConfigError('"exp" property of floating point number type object\'s "size" property must be an integer')

                if exp < 1:
                    raise ConfigError('invalid floating point number exponent size: {}')

                obj.exp_size = exp

            if 'mant' in size:
                mant = size['mant']

                if not _is_int_prop(mant):
                    raise ConfigError('"mant" property of floating point number type object\'s "size" property must be an integer')

                if mant < 1:
                    raise ConfigError('invalid floating point number mantissa size: {}')

                obj.mant_size = mant

        # align
        if 'align' in node:
            align = node['align']

            if not _is_int_prop(align):
                raise ConfigError('"align" property of floating point number type object must be an integer')

            if not _is_valid_alignment(align):
                raise ConfigError('invalid alignment: {}'.format(align))

            obj.align = align

        # byte order
        if 'byte-order' in node:
            byte_order = node['byte-order']

            if not _is_str_prop(byte_order):
                raise ConfigError('"byte-order" property of floating point number type object must be a string ("le" or "be")')

            byte_order = _byte_order_str_to_bo(byte_order)

            if byte_order is None:
                raise ConfigError('invalid "byte-order" property in floating point number type object')
        else:
            byte_order = self._bo

        obj.byte_order = byte_order

        return obj

    def _create_enum(self, obj, node):
        if obj is None:
            # create enumeration object
            obj = metadata.Enum()

        unk_prop = _get_first_unknown_type_prop(node, [
            'value-type',
            'members',
        ])

        if unk_prop:
            raise ConfigError('unknown enumeration type object property: "{}"'.format(unk_prop))

        # value type
        if 'value-type' in node:
            try:
                obj.value_type = self._create_type(node['value-type'])
            except Exception as e:
                raise ConfigError('cannot create enumeration type\'s integer type', e)

        # members
        if 'members' in node:
            members_node = node['members']

            if not _is_array_prop(members_node):
                raise ConfigError('"members" property of enumeration type object must be an array')

            cur = 0

            for index, m_node in enumerate(members_node):
                if not _is_str_prop(m_node) and not _is_assoc_array_prop(m_node):
                    raise ConfigError('invalid enumeration member #{}: expecting a string or an associative array'.format(index))

                if _is_str_prop(m_node):
                    label = m_node
                    value = (cur, cur)
                    cur += 1
                else:
                    if 'label' not in m_node:
                        raise ConfigError('missing "label" property in enumeration member #{}'.format(index))

                    label = m_node['label']

                    if not _is_str_prop(label):
                        raise ConfigError('"label" property of enumeration member #{} must be a string'.format(index))

                    if 'value' not in m_node:
                        raise ConfigError('missing "value" property in enumeration member ("{}")'.format(label))

                    value = m_node['value']

                    if not _is_int_prop(value) and not _is_array_prop(value):
                        raise ConfigError('invalid enumeration member ("{}"): expecting an integer or an array'.format(label))

                    if _is_int_prop(value):
                        cur = value + 1
                        value = (value, value)
                    else:
                        if len(value) != 2:
                            raise ConfigError('invalid enumeration member ("{}"): range must have exactly two items'.format(label))

                        mn = value[0]
                        mx = value[1]

                        if mn > mx:
                            raise ConfigError('invalid enumeration member ("{}"): invalid range ({} > {})'.format(label, mn, mx))

                        value = (mn, mx)
                        cur = mx + 1

                obj.members[label] = value

        return obj

    def _create_string(self, obj, node):
        if obj is None:
            # create string object
            obj = metadata.String()

        unk_prop = _get_first_unknown_type_prop(node, [
            'encoding',
        ])

        if unk_prop:
            raise ConfigError('unknown string type object property: "{}"'.format(unk_prop))

        # encoding
        if 'encoding' in node:
            encoding = node['encoding']

            if not _is_str_prop(encoding):
                raise ConfigError('"encoding" property of string type object must be a string ("none", "ascii", or "utf-8")')

            encoding = _encoding_str_to_encoding(encoding)

            if encoding is None:
                raise ConfigError('invalid "encoding" property in string type object')

            obj.encoding = encoding

        return obj

    def _create_struct(self, obj, node):
        if obj is None:
            # create structure object
            obj = metadata.Struct()

        unk_prop = _get_first_unknown_type_prop(node, [
            'min-align',
            'fields',
        ])

        if unk_prop:
            raise ConfigError('unknown string type object property: "{}"'.format(unk_prop))

        # minimum alignment
        if 'min-align' in node:
            min_align = node['min-align']

            if not _is_int_prop(min_align):
                raise ConfigError('"min-align" property of structure type object must be an integer')

            if not _is_valid_alignment(min_align):
                raise ConfigError('invalid minimum alignment: {}'.format(min_align))

            obj.min_align = min_align

        # fields
        if 'fields' in node:
            fields = node['fields']

            if not _is_assoc_array_prop(fields):
                raise ConfigError('"fields" property of structure type object must be an associative array')

            for field_name, field_node in fields.items():
                if not is_valid_identifier(field_name):
                    raise ConfigError('"{}" is not a valid field name for structure type'.format(field_name))

                try:
                    obj.fields[field_name] = self._create_type(field_node)
                except Exception as e:
                    raise ConfigError('cannot create structure type\'s field "{}"'.format(field_name), e)

        return obj

    def _create_array(self, obj, node):
        if obj is None:
            # create array object
            obj = metadata.Array()

        unk_prop = _get_first_unknown_type_prop(node, [
            'length',
            'element-type',
        ])

        if unk_prop:
            raise ConfigError('unknown array type object property: "{}"'.format(unk_prop))

        # length
        if 'length' in node:
            length = node['length']

            if not _is_int_prop(length) and not _is_str_prop(length):
                raise ConfigError('"length" property of array type object must be an integer or a string')

            if type(length) is int and length < 0:
                raise ConfigError('invalid static array length: {}'.format(length))

            obj.length = length

        # element type
        if 'element-type' in node:
            try:
                obj.element_type = self._create_type(node['element-type'])
            except Exception as e:
                raise ConfigError('cannot create array type\'s element type', e)

        return obj

    def _create_variant(self, obj, node):
        if obj is None:
            # create variant object
            obj = metadata.Variant()

        unk_prop = _get_first_unknown_type_prop(node, [
            'tag',
            'types',
        ])

        if unk_prop:
            raise ConfigError('unknown variant type object property: "{}"'.format(unk_prop))

        # tag
        if 'tag' in node:
            tag = node['tag']

            if not _is_str_prop(tag):
                raise ConfigError('"tag" property of variant type object must be a string')

            # do not validate variant tag for the moment; will be done in a
            # second phase
            obj.tag = tag

        # element type
        if 'types' in node:
            types = node['types']

            if not _is_assoc_array_prop(types):
                raise ConfigError('"types" property of variant type object must be an associative array')

            # do not validate type names for the moment; will be done in a
            # second phase
            for type_name, type_node in types.items():
                if not is_valid_identifier(type_name):
                    raise ConfigError('"{}" is not a valid type name for variant type'.format(type_name))

                try:
                    obj.types[type_name] = self._create_type(type_node)
                except Exception as e:
                    raise ConfigError('cannot create variant type\'s type "{}"'.format(type_name), e)

        return obj

    def _create_type(self, type_node):
        if type(type_node) is str:
            t = self._lookup_type_alias(type_node)

            if t is None:
                raise ConfigError('unknown type alias "{}"'.format(type_node))

            return t

        if not _is_assoc_array_prop(type_node):
            raise ConfigError('type objects must be associative arrays')

        if 'inherit' in type_node and 'class' in type_node:
            raise ConfigError('cannot specify both "inherit" and "class" properties in type object')

        if 'inherit' in type_node:
            inherit = type_node['inherit']

            if not _is_str_prop(inherit):
                raise ConfigError('"inherit" property of type object must be a string')

            base = self._lookup_type_alias(inherit)

            if base is None:
                raise ConfigError('cannot inherit from type alias "{}": type alias does not exist'.format(inherit))

            func = self._type_to_create_type_func[type(base)]
        else:
            if 'class' not in type_node:
                raise ConfigError('type objects which do not inherit must have a "class" property')

            class_name = type_node['class']

            if type(class_name) is not str:
                raise ConfigError('type objects\' "class" property must be a string')

            if class_name not in self._class_name_to_create_type_func:
                raise ConfigError('unknown type class "{}"'.format(class_name))

            base = None
            func = self._class_name_to_create_type_func[class_name]

        return func(base, type_node)

    def _yaml_ordered_load(self, stream):
        class OLoader(yaml.Loader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)

            return collections.OrderedDict(loader.construct_pairs(node))

        OLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                                construct_mapping)

        return yaml.load(stream, OLoader)

    def parse(self, yml):
        try:
            root = self._yaml_ordered_load(yml)
        except Exception as e:
            raise ConfigError('cannot parse YAML input', e)

        root_type = self._create_type(root)

        return Config(root_type)


def from_yaml(yml):
    parser = _YamlConfigParser()
    cfg = parser.parse(yml)

    return cfg


def from_yaml_file(path):
    try:
        with open(path) as f:
            return from_yaml(f.read())
    except Exception as e:
        raise ConfigError('cannot create configuration from YAML file'.format(e), e)
