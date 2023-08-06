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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


"""Module for generating Wiki docs"""

class WikiOutput:
    """Generates Wiki from documentation model"""

    def __init__(self):
        pass

    def generate_output(self, parsed_items):
        """Returns generated Wiki string"""
        output = ''

        root_item = parsed_items[0]
        last_level = 0
        for item in parsed_items:
            level = item['level']
            output += '*' * level
            output += self.__get_wiki_item(item)
            output += '.\n'
            is_root = False
        return output

    def __get_wiki_item(self, item):
        retval = ''
        retval += '{} '.format(item['name'])
        retval += '[{}] '.format(item['type'])
        retval += '{} '.format(self.__get_required_field(item))
        return retval

    def __get_required_field(self, parsed_item):
        return 'required' if parsed_item['required'] else ''
