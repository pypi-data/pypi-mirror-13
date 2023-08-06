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


"""Module for generating HTML docs"""

class HtmlOutput:
    """Generates HTML from documentation model"""

    def __init__(self):
        pass

    def generate_output(self, parsed_items):
        """Returns generated HTML string"""
        return self.__get_html_begin() + \
                self.__get_html_middle(parsed_items) + \
                self.__get_html_end()

    def __get_html_middle(self, parsed_items):
        output = ''
        root_item = parsed_items[0]

        output += '<h1 class="root_title">{}</h1>\n'.format(root_item['title'])
        output += '<p class="root_description">{}</p>\n'.format(root_item['description'])

        output += '<ul class="level0">\n'
        last_level = 0
        is_root = True
        for item in parsed_items:
            level = item['level']
            if last_level < level:
                output += '<ul class="level{}">\n'.format(level)
            for i in range(last_level - level):
                output += '</ul>\n'
            last_level = level
            output += self.__get_html_item(item, is_root)
            is_root = False
        output += '</ul>\n'
        return output

    def __get_required_field(self, parsed_item):
        return 'required' if parsed_item['required'] else ''

    def __get_html_item(self, parsed_item, is_root):
        retval = '<li class="schema_item"> \n'
        retval += '<div class="name">{}</div> \n'.format(parsed_item['name'])
        retval += '<div class="type">[{}]</div> \n'.format(parsed_item['type'])
        retval += '<div class="required">{}</div> \n'.format(self.__get_required_field(parsed_item))
        retval += '<div class="docs">\n' if not is_root else '<div class="root_docs">'
        retval += '<div class="title">{}</div>\n'.format(parsed_item['title'])
        retval += ': ' if parsed_item['title'] != '' and parsed_item['description'] != '' else ''
        retval += '<div class="description">{}</div>\n'.format(parsed_item['description'])
        retval += '</div>\n'
        retval += '</li>\n'
        return retval
     
    def __get_html_begin(self):
        return '<html><head><link rel="stylesheet" type="text/css" href="style.css" /></head><body>\n'

    def __get_html_end(self):
        return '</body></html>'
