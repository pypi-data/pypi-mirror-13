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
import socket
import variance
from endure.database import Database


class Endure(dict):
    """
        Database engine.
    """

    def __init__(self, ip_address="127.0.0.1", port=8850, debug=False):
        super(dict)
        dict.__init__({})
        self.config = variance.Variance()
        self.config.from_dict(default_config)
        if ip_address != "127.0.0.1":
            self.ip_address = ip_address
        if port != 8850:
            self.port = port

        self.ip_address = ip_address
        self.port = port
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_client = False
        self.is_server = False

    def listen(self):
        if not self.is_client:
            self.is_server = True
            self.socket.bind((self.ip_address, self.port))
        else:
            if self.debug:
                print("DEBUG: We are already connected to a remote host.")

    def connect(self):
        if not self.is_server:
            self.socket.connect((self.ip_address, self.port))
        else:
            if self.debug:
                print("DEBUG: We are already listening for client connections.")

    def create_database(self, name):
        if len(name):
            if not self.get(name):
                self[name] = Database(name)

default_config = {
    'USERNAME': 'change_me',
    'PASSWORD': 'change_me',
    'HOST': '127.0.0.1',
    'PORT': 8850,
    'BUFFER_SIZE': 4096,
    'DEBUG': True,
    'LOGGING': True
}
