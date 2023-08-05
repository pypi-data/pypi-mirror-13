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


def length(value, minimum=0, maximum=0):
    valid = True
    value_type = type(value)
    if value_type != int and value_type != str and value_type != float:
        return False
    if minimum != 0:
        if value_type == int or value_type == float:
            if value < minimum:
                valid = False
        elif value_type == str:
            if len(value) < minimum:
                valid = False
    if maximum != 0:
        if value_type == int or value_type == float:
            if value > maximum:
                valid = False
        elif value_type == str:
            if len(value) > maximum:
                valid = False
    return valid


def nullable(value, can_null=True):
    if not can_null:
        if value is None:
            return False
    return True

options = {
    'length': {
            'args': ['minimum', 'maximum'],
            'arg_types': [int, float],
            'types': [int, float, str],
            'constraint': True,
            'func': length
    },
    'nullable': {
        'args': ['can_null'],
        'arg_types': [bool, ],
        'types': [bool, int, float, str],
        'constraint': True,
        'func': nullable
    },
}
