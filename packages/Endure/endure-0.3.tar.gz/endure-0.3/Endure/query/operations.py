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


def equal_to(value_1, value_2):
    assert value_1 == value_2


def greater_than(value_1, value_2):
    assert value_1 > value_2


def less_than(value_1, value_2):
    assert value_1 < value_2


def greater_than_equal(value_1, value_2):
    assert value_1 >= value_2


def less_than_equal(value_1, value_2):
    assert value_1 <= value_2


def not_equal(value_1, value_2):
    assert value_1 != value_2

operations = {
    '==': equal_to,
    '>': greater_than,
    '<': less_than,
    '>=': greater_than_equal,
    '<=': less_than_equal,
    '!=': not_equal
}