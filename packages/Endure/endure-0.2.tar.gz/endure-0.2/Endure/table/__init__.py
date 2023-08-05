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
import hashlib
from endure.column import Column, options


class Table(dict):
    """
    The table class, why not use a dict?
    """
    def __init__(self, name, iterable=None, file_name=None, file_extension=None):
        super(dict)
        this_dict = {}
        if type(name) is str:
            if len(name) > 0:
                self.name = name
            else:
                raise ValueError("Table name must not be null")
        else:
            raise ValueError("Table name must be string")
        self.rows = {}
        self.deleted_row_ids = []
        if iterable is not None:
            if type(iterable) is dict:
                for key, value in iterable.items():
                    this_dict[key] = value
        dict.__init__(this_dict)

    def add_column(self, column_or_name, column_type=None):
        col_type = type(column_or_name)
        if col_type == Column:
            self[column_or_name.name] = column_or_name
        elif col_type == str and column_type is not None:
            new_column = Column(column_or_name, column_type)
            self[column_or_name] = new_column
        else:
            raise ValueError("Cannot add non-column value without name and type specified")
        return True

    def add_row(self, data):
        new_row = {}
        valid = True
        for key, value in data.items():

            if key in self.keys():
                print key
                print value

                for constraint in self[key].constraints:
                    print constraint
                    print self
                    print self[key][constraint]
                    if not options[constraint]['func'](value, **self[key][constraint]):
                        raise ValueError("%s constaint failed for column %s" % (constraint, key))
                if valid:
                    new_row[key] = value
            else:
                raise KeyError("Column %s is not in table" % key)
        if valid:
            if len(self.deleted_row_ids) == 0:
                if len(self.rows.keys()) > 0:
                    next_key = max(self.rows.keys()) + 1
                else:
                    next_key = 0
                self.rows[next_key] = new_row
            else:
                self.rows[self.deleted_row_ids.pop()] = new_row
            return True
        return False

    def get_row_by_id(self, key):
        if self.rows.get(key):
            return self.rows[key]
        else:
            raise KeyError("Row not found")

    def drop_row_by_id(self, key):
        if self.rows.get(key):
            self.rows.pop(key)
            self.deleted_row_ids.append(key)
        else:
            raise KeyError("Row not found")
        return True

    def drop_column(self, name):
        if self.get(name):
            self.pop(name)
        else:
            raise ValueError("Column %s not in table" % name)
        return True

    def hashed(self):
        return hashlib.md5(self)
