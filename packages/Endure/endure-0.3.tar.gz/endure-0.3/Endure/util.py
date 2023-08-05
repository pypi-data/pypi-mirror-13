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
import os
from datetime import datetime


def safe_path(file_path):
    if '/' in file_path or '\\' in file_path:
        if file_path.startswith(os.getcwd()) and \
                        '..' not in file_path and '~' not in file_path and \
                        ';' not in file_path and '&' not in file_path and \
                        './' not in file_path:
            return True
    else:
        return True
    return False


def log_file_name(file_name="anircbot", file_extension='.log'):
    now = datetime.now()
    if file_name == '' or not safe_path(file_name):
        file_name = 'anircbot'
    if file_extension == '' or not safe_path(file_extension):
        file_extension = '.log'
    return file_name + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + file_extension