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


"""Generates documentation from JSON Schema"""

__version__ = '0.1.1'

import argparse

from jschemadoc import docsmodel
from jschemadoc import html_output
from jschemadoc import wiki_output


if __name__ == '__main__':
    output_generators = {
        'html': html_output.HtmlOutput,
        'wiki': wiki_output.WikiOutput
    }

    parser = argparse.ArgumentParser(
        description='JSchemaDoc generates documentation from JSON Schema file')
    parser.add_argument('schema', help='JSON Schema input')
    parser.add_argument('output_type', choices=output_generators.keys(), help='Output type')
    parser.add_argument('output', help='Output file')
    parser.add_argument('-V', '--version', action='version', version='{}'.format(__version__))
    args = parser.parse_args()

    schema = docsmodel.get_schema_from_file(args.schema)
    parsed_items = docsmodel.DocsModel().parse(schema)

    output_generator = output_generators[args.output_type]()
    output = output_generator.generate_output(parsed_items)

    with open(args.output, 'wt') as f:
        f.write(output)
