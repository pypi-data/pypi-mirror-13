# JSchemaDoc library and tool for generating documentation from JSON Schemas.
# Copyright (C) 2015  Maciej Szymański
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, version 2.1
# of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import collections
import json


def get_schema_from_file(file_name):
    """Returns parsed JSON file contents"""
    with open(file_name, 'rt') as schema_file:
        json_str = schema_file.read()
    return json.loads(json_str, object_pairs_hook=collections.OrderedDict)


class ParsedItem(dict):
    """Parsed schema item"""

    def __init__(self, json_object, name, required, level):
        """Fills dict with basic item information."""
        super().__init__()
        self['name'] = name
        self['title'] = json_object.get('title', '')
        self['type'] = json_object.get('type')
        self['description'] = json_object.get('description', '')
        self['level'] = level
        self['required'] = required

    def block__repr__(self):
        return '{} [{}] {}'.format(self['name'], self['type'], self['level'])


class DocsModel:
    """Schema parser and documentation model"""

    def __init__(self):
        self.__parsed_items = None

    def parse(self, json_object):
        """Returns multi-level list of parsed items.
        Parsing is done recursively.
        """
        self.__parsed_items = list()
        self.__parse_schema(json_object, 'root', True, 0)
        return self.__parsed_items

    def __parse_schema(self, schema, name, required, level):
        """Parses schema, which type is object, array or leaf.
        Appends new ParsedItem to self.__parsed_items list.
        """
        parsed_item = ParsedItem(schema, name, required, level)
        self.__parsed_items.append(parsed_item)
        required = schema.get('required', [])

        if 'enum' in schema:
            parsed_item['enum'] = schema.get('enum')
        item_type = schema.get('type')
        if item_type == 'object':
            self.__parse_object(parsed_item, schema, required, level)
        elif item_type == 'array':
            self.__parse_array(parsed_item, schema, required, level)
        else:
            parse_leaf(parsed_item, schema)

    def __parse_object(self, parsed_item, schema, required, level):
        """Parses schema of type object."""
        for key, value in schema.get('properties', {}).items():
            self.__parse_schema(value, key, key in required, level + 1)

    def __parse_array(self, parsed_item, schema, required, level):
        """Parses schema of type array."""
        items = schema.get('items')
        parsed_item['minItems'] = schema.get('minItems', None)
        parsed_item['maxItems'] = schema.get('maxItems', None)
        parsed_item['uniqueItems'] = schema.get('uniqueItems', False)
        if isinstance(items, dict):
            # items is single schema describing all elements in an array
            self.__parse_schema(
                items,
                'array item',
                required,
                level + 1)

        elif isinstance(items, list):
            # items is list of schemas,
            # each describing element on given position
            for index, list_item in enumerate(items):
                self.__parse_schema(
                    list_item,
                    'array item {}'.format(index),
                    index in required,
                    level + 1)


def parse_leaf(parsed_item, schema):
    """Parses schema of: number, integer, string, boolean, enum."""
    if parsed_item['type'] in ('number', 'integer'):
        parsed_item['minimum'] = schema.get('minimum', '-inf')
        parsed_item['maximum'] = schema.get('maximum', '+inf')
        parsed_item['exclusiveMinimum'] = schema.get('exclusiveMinimum', False)
        parsed_item['exclusiveMaximum'] = schema.get('exclusiveMaximum', False)
    elif parsed_item['type'] in ('string', ):
        parsed_item['minLength'] = schema.get('minLength', None)
        parsed_item['maxLength'] = schema.get('maxLength', None)
        parsed_item['pattern'] = schema.get('pattern', None)
        parsed_item['format'] = schema.get('format', None)
