"""
    Endure - A python database

    Author: Bill Schumacher <bill@servernet.co>
    License: LGPLv3
    Copyright: 2015 Bill Schumacher, Cerebral Power

** GNU Lesser General Public License Usage
** This file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPLv3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl.html.
"""
from endure.column.options import options


class Column(dict):
    """
    The column class, why not use a dict?
    """
    def __init__(self, name, column_type, iterable=None):
        super(dict)
        this_dict = {}
        if iterable:
            if type(iterable) is dict:
                for key, value in iterable.items():
                    this_dict[key] = value
        dict.__init__(this_dict)
        self.name = name
        self.constraints = []
        self.type = None
        if isinstance(column_type, str):
            column_type = column_type.lower()
            if column_type == "str" or column_type == "string" or column_type == 'char' or column_type == 'varchar' or \
                column_type == 'blob' or column_type == 'text' or column_type == 'longtext':
                column_type = str
            elif column_type == 'int' or column_type == 'integer' or column_type == 'longint' or 'number':
                column_type = int
            elif column_type == 'float' or column_type == 'double':
                column_type = float
            else:
                raise ValueError('Column type %s is not supported.' % column_type)
        if column_type in column_types:
            self.type = column_type
        else:
            raise ValueError("Column type %s is not supported." % str(column_type))

    def add_option(self, name, **values):
        if options.get(name):
            option = options[name]
            if self.type in option['types']:
                self[name] = {}
                for key, value in values.items():
                    if key in options[name]['args']:
                        if type(value) in options[name]['arg_types']:
                            self[name][key] = value
                        else:
                            raise ValueError('Invalid type %s for option %s argument %s' % (str(type(value)), name, key))
                    else:
                        raise ValueError('Invalid argument %s for option %s' % (key, name))
            else:
                raise ValueError('Option is not supported for column type %s' % str(self.type))
            if option['constraint']:
                self.constraints.append(name)
            return True
        else:
            raise ValueError('Option %s does not exist' % name)

    def remove_option(self, name):
        if self.get(name):
            if self[name]['constraint']:
                self.constraints.pop(self[name])
            self.pop(name)
            return True
        raise ValueError('Option %s is not present on column' % name)

    def supported_options(self):
        option_list = []
        for option in options:
            if self.type in option['types']:
                option_list.append(option)
        return option_list


column_types = [bool, int, float, str]
