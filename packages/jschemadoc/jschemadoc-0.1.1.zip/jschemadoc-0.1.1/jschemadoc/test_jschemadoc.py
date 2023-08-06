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


"""Tests for jschemadoc"""


import unittest

import jschemadoc


class TestParsedItem(unittest.TestCase):
    """Tests ParsedItem class."""

    def setUp(self):
        json_obj = {
            'title': 'test_title',
            'type': 'test_type',
            'description': 'test_desc'}
        self.pi = jschemadoc.ParsedItem(json_obj, 'test_name', True, 0)

    def test_is_dict(self):
        self.assertIsInstance(self.pi, dict)

    def test_set_basic_object_docs(self):
        self.assertEqual(self.pi['name'], 'test_name')
        self.assertEqual(self.pi['title'], 'test_title')
        self.assertEqual(self.pi['type'], 'test_type')
        self.assertEqual(self.pi['description'], 'test_desc')
        self.assertEqual(self.pi['level'], 0)
        self.assertEqual(self.pi['required'], True)


basic_type_schemas_PI_count = {
        'null': 2,
        'number': 2,
        'integer': 2,
        'string': 2,
        'simple_object': 4
        }

schema_to_array_items_type = {
        'null': 'null',
        'number': 'number',
        'integer': 'integer',
        'string': 'string',
        'simple_object': 'object'
        }


class TestDocsModelBT_simple_object(unittest.TestCase):

    def setUp(self):
        self.dm = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
                'test_schemas/simple_object.json')
        self.parsed_items = self.dm.parse(self.schema)

    def test_root_element(self):
        """Tests if root entry is generated correctly."""
        item = jschemadoc.ParsedItem(
            {
                'title': 'simple_object',
                'type': 'object',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        self.assertEqual(self.parsed_items[0], item)

    def test_first_name(self):
        item = jschemadoc.ParsedItem(
            {'title': '', 'type': 'string', 'description': ''},
            'firstName',
            True,
            1)
        item['pattern'] = None
        item['minLength'] = None
        item['maxLength'] = None
        item['format'] = None
        self.assertEqual(self.parsed_items[1], item)

    def test_last_name(self):
        item = jschemadoc.ParsedItem(
            {'title': '', 'type': 'string', 'description': 'Last name'},
            'lastName',
            False,
            1)
        item['pattern'] = None
        item['minLength'] = None
        item['maxLength'] = None
        item['format'] = None
        self.assertEqual(self.parsed_items[2], item)


class TestDocsModelBT_boolean(unittest.TestCase):

    def setUp(self):
        self.dm = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/boolean.json')
        self.parsed_items = self.dm.parse(self.schema)

    def test_exactly_one_ParsedItem_is_generated(self):
        self.assertEqual(len(self.parsed_items), 1)

    def test_boolean(self):
        pi = jschemadoc.ParsedItem(
            {
                'title': 'boolean',
                'description': 'Example schema description.',
                'type': 'boolean'
            },
            'root',
            True,
            0)
        self.assertEqual(self.parsed_items[0], pi)


class TestDocsModelBT_integer(unittest.TestCase):

    def setUp(self):
        self.docs_model = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/integer.json')
        self.parsed_items = self.docs_model.parse(self.schema)

    def test_exactly_one_ParsedItem_is_generated(self):
        self.assertEqual(len(self.parsed_items), 1)

    def test_integer(self):
        pi = jschemadoc.ParsedItem(
            {
                'title': 'integer',
                'type': 'integer',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        pi['minimum'] = 3
        pi['maximum'] = 10
        pi['exclusiveMinimum'] = True
        pi['exclusiveMaximum'] = False
        self.assertEqual(self.parsed_items[0], pi)


class TestDocsModelBT_number(unittest.TestCase):
    """Tests parsing of number schema"""

    def setUp(self):
        self.dm = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
                'test_schemas/number.json')
        self.parsed_items = self.dm.parse(self.schema)

    def test_exactly_one_ParsedItem_is_generated(self):
        self.assertEqual(len(self.parsed_items), 1)

    def test_number(self):
        item = jschemadoc.ParsedItem(
            {
                'title': 'number',
                'type': 'number',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        item['minimum'] = 3
        item['maximum'] = 10
        item['exclusiveMinimum'] = True
        item['exclusiveMaximum'] = False
        self.assertEqual(self.parsed_items[0], item)


class TestDocsModelBT_number_defaults(unittest.TestCase):
    """Tests parsing of number schema defaults"""

    def setUp(self):
        self.dm = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
                'test_schemas/number_defaults.json')
        self.parsed_items = self.dm.parse(self.schema)

    def test_exactly_one_ParsedItem_is_generated(self):
        self.assertEqual(len(self.parsed_items), 1)

    def test_number(self):
        item = jschemadoc.ParsedItem(
            {
                'title': 'number_defaults',
                'type': 'number',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        item['minimum'] = '-inf'
        item['maximum'] = '+inf'
        item['exclusiveMinimum'] = False
        item['exclusiveMaximum'] = False
        self.assertEqual(self.parsed_items[0], item)


class TestDocsModelBT_null(unittest.TestCase):
    """Tests schema of type null."""

    def setUp(self):
        self.dm = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
                'test_schemas/null.json')
        self.parsed_items = self.dm.parse(self.schema)

    def test_exactly_one_ParsedItem_is_generated(self):
        self.assertEqual(len(self.parsed_items), 1)

    def test_null(self):
        """Tests null schema parsing."""
        item = jschemadoc.ParsedItem(
            {
                'title': 'null',
                'type': 'null',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        self.assertEqual(self.parsed_items[0], item)


class TestDocsModelBTString(unittest.TestCase):

    def setUp(self):
        self.docs_model = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/string.json')
        self.parsed_items = self.docs_model.parse(self.schema)

    def test_exactly_one_entry(self):
        """Tests if sigle schema generates one entry in model"""
        self.assertEqual(len(self.parsed_items), 1)

    def test_string(self):
        """Tests parsing string schema model"""
        item = jschemadoc.ParsedItem(
            {
                'title': 'string',
                'type': 'string',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        item['minLength'] = 1
        item['maxLength'] = 20
        item['pattern'] = '^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$'
        item['format'] = 'hostname'
        self.assertEqual(self.parsed_items[0], item)


class TestDocsModelBTStringDefaults(unittest.TestCase):
    """Tests if not explicitly given params of type string
    have correct values.
    """

    def setUp(self):
        self.docs_model = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/string_defaults.json')
        self.parsed_items = self.docs_model.parse(self.schema)

    def test_exactly_one_entry(self):
        """Tests if sigle schema generates one entry in model"""
        self.assertEqual(len(self.parsed_items), 1)

    def test_string(self):
        """Tests parsing string schema model"""
        item = jschemadoc.ParsedItem(
            {
                'title': 'string_defaults',
                'type': 'string',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        item['minLength'] = None
        item['maxLength'] = None
        item['pattern'] = None
        item['format'] = None
        self.assertEqual(self.parsed_items[0], item)


class TestDocsModelBT_array_list(unittest.TestCase):

    def setUp(self):
        self.docs_model = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/array_list.json')

    def test_exactly_one_entry_is_generated(self):
        """Test if one entry is generated"""
        for schema_name, expected_number in basic_type_schemas_PI_count.items():
            schema = self.schema
            schema['items'] = jschemadoc.get_schema_from_file(
                'test_schemas/' + schema_name + '.json')
            parsed_items = self.docs_model.parse(schema)
            self.assertTrue(
                expected_number == len(parsed_items),
                'For {} expected {} parsed items, got {}'.format(
                    schema_name, expected_number, len(parsed_items)))

    def test_array_root(self):
        schema = self.schema
        parsed_items = self.docs_model.parse(schema)
        item = jschemadoc.ParsedItem(
            {
                'title': 'array_list',
                'type': 'array',
                'description': 'Example schema description.'
            },
            'root',
            True,
            0)
        item['minItems'] = 1
        item['maxItems'] = 10
        item['uniqueItems'] = False
        for item, value in item.items():
            self.assertEqual(parsed_items[0][item], value)

    def test_array_every_item_type(self):
        """Checks if array entries match schema"""
        for schema_name, expected_type in schema_to_array_items_type.items():
            schema = self.schema
            schema['items'] = jschemadoc.get_schema_from_file(
                'test_schemas/' + schema_name + '.json')
            parsed_items = self.docs_model.parse(schema)
            self.assertTrue(expected_type == parsed_items[1]['type'])


class TestDocsModelBT_array_tuple(unittest.TestCase):
    """Tests array tuple typing."""

    def setUp(self):
        """Tests set up."""
        self.docs_model = jschemadoc.DocsModel()
        self.schema = jschemadoc.get_schema_from_file(
            'test_schemas/array_tuple.json')

    def test_entries_count(self):
        """Tests if no extra entries are generated."""
        entries = self.docs_model.parse(self.schema)
        self.assertEqual(4, len(entries))

    def test_root(self):
        """Tests array tuple root element."""
        entries = self.docs_model.parse(self.schema)
        root_entry = entries[0]
        good_root = jschemadoc.ParsedItem(
            {
                "title": "array_tuple",
                "description": "Example schema description.",
                "type": "array"
            },
            'root',
            True,
            0)
        good_root['uniqueItems'] = False
        good_root['minItems'] = None
        good_root['maxItems'] = None

        self.assertEqual(root_entry, good_root)

    def test_other_entries(self):
        # TODO: test for required field
        entries = self.docs_model.parse(self.schema)
        good_entries = list()
        good_entries.append(jschemadoc.ParsedItem(
            {
                'title': '',
                'description': '',
                'type': 'number'
            },
            'array item 0',
            False,
            1))
        good_entries[0]['maximum'] = '+inf'
        good_entries[0]['minimum'] = '-inf'
        good_entries[0]['exclusiveMinimum'] = False
        good_entries[0]['exclusiveMaximum'] = False

        good_entries.append(jschemadoc.ParsedItem(
            {
                'title': '',
                'description': '',
                'type': 'string'
            },
            'array item 1',
            False,
            1))
        good_entries[1]['minLength'] = None
        good_entries[1]['maxLength'] = None
        good_entries[1]['pattern'] = None
        good_entries[1]['format'] = None

        good_entries.append(jschemadoc.ParsedItem(
            {
                'title': '',
                'description': '',
                'type': 'boolean'
            },
            'array item 2',
            False,
            1))

        self.assertEqual(good_entries[0], entries[1])
        self.assertEqual(good_entries[1], entries[2])
        self.assertEqual(good_entries[2], entries[3])


# class TestDocsModelBT_multilevel_schemas(unittest.TestCase):


def print_compare_dicts(dict1, dict2):
    all_keys = list(dict1.keys()) + list(dict2.keys())
    unique_keys = set(all_keys)
    for key in unique_keys:
        print('{}: {} {}\n'.format(
            key, dict1.get(key, 'N/A'), dict2.get(key, 'N/A')))


if __name__ == '__main__':
    unittest.main()
