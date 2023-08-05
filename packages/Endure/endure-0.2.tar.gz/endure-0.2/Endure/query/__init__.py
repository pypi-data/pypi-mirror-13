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
from endure.query.operations import operations


class Query:
    def __init__(self, table):
        self.table = table
        self.rows = table.rows

    def filter(self, column, operation, operation_value):
        rows = {}
        for key, value in self.rows.items():
            if operations[operation](value[column], operation_value):
                rows[key] = value
        self.rows = rows
        return self

    def filter_string(self, string):
        split_string = string.split()
        if len(split_string) > 3:
            raise ValueError("A filter should have no more than 3 arguments")
        return self.filter(split_string[0], split_string[1], split_string[2])

    def first(self):
        return self.rows.pop(0)

    def last(self):
        return self.rows.pop()

    def get(self, index):
        return self.rows[index]
