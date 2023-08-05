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
import ast
import os
from endure.table import Table
from endure.util import safe_path, log_file_name
from datetime import datetime


class Database(dict):
    """
    The database class, why not use a dict?
    """
    def __init__(self, name, iterable=None, file_name=None, file_extension=None):
        super(dict)
        this_dict = {}
        self.name = name
        if iterable:
            if type(iterable) is dict:
                for key, value in iterable.items():
                    this_dict[key] = value
        dict.__init__(this_dict)
        self.now = datetime.now()
        if file_name:
            self.file_name = file_name
        else:
            self.file_name = self.name
        if file_extension:
            self.file_extension = file_extension
        else:
            self.file_extension = ".db"
        self.current_file = log_file_name(self.file_name, self.file_extension)
        if os.path.isfile(self.current_file):
            self.from_file(self.file_name, self.file_extension)
        else:
            pass

    def from_file(self, file_name=None, file_extension='.db'):
        if file_name is None:
            file_name = self.name
        try:
            file_path = log_file_name(file_name, file_extension)
            if safe_path(file_path):
                with open(file_path, 'r') as db_file:
                    db_string = db_file.read()
                    lines = db_string.split('\n')
                    for line in lines:
                        if line:
                            line_split = line.split('=')
                            if len(line_split):
                                self[line_split[0]] = ast.literal_eval(line_split[1])
                    db_file.close()
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            if len(ex.args):
                errno, strerror = ex.args
                print("Error %s: %s" % (errno, strerror))
                return "Error %s: %s" % (errno, strerror)
            else:
                print("Error: %s" % ex.message)
                return "Error: %s" % ex.message
        return "Success"

    def to_file(self, file_path=None):
        try:
            if file_path is None:
                file_path = self.current_file
            if safe_path(file_path):
                with open(file_path, 'a') as db_file:
                    db_file.seek(0)
                    db_file.truncate()
                    for key, value in self.items():
                        db_file.write(key + '=' + value.__str__() + '\n')
                    db_file.close()
                print("Database saved.")
                return "Database saved."
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            if len(ex.args):
                errno, strerror = ex.args
                print("Error %s: %s" % (errno, strerror))
                return "Error: %s" % strerror
            else:
                print("Error: %s" % ex.message)
                return "Error: %s" % ex.message

    def add_table(self, name, columns=None):
        if columns is not None:
            new_table = Table(name, columns)
        else:
            new_table = Table(name)
        if new_table is not None:
            self[name] = new_table
            return True
        raise RuntimeError("Unable to create table %s" % name)

    def drop_table(self, name):
        if name in self.keys():
            self.pop(name)
            return True
        else:
            raise KeyError("Table %s does not exist" % name)

