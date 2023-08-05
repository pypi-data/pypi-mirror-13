"""
    Variance - A python configuration manager

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
from variance.util import safe_path


class Variance(dict):
    """
    Configuration Manager
    """
    def __init__(self, iterable=None):
        super(dict)
        if type(iterable) != dict:
            iterable = {}
        dict.__init__({})
        self.from_dict(iterable)

    def from_dict(self, iterable):
        if type(iterable) != dict:
            return False
        for key, value in iterable.items():
            self[key] = value
        return True

    def from_file(self, file_path='default.cfg'):
        try:
            if file_path == '':
                file_path = 'default.cfg'
            if safe_path(file_path):
                with open(file_path, 'r') as config_file:
                    config_string = config_file.read()
                    lines = config_string.split('\n')
                    for line in lines:
                        if line:
                            line_split = line.split('=')
                            if len(line_split):
                                self[line_split[0]] = ast.literal_eval(line_split[1])
                    config_file.close()
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            errno, strerror = ex.args
            print("Error %s: %s" % (errno, strerror))
        return "Success"

    def to_file(self, file_path='default.cfg'):
        try:
            if file_path == '':
                file_path = 'default.cfg'
            if safe_path(file_path):
                with open(file_path, 'a') as config_file:
                    config_file.seek(0)
                    config_file.truncate()
                    for key, value in self.items():
                        if type(value) is not str:
                            config_file.write(key + '=' + value.__str__() + '\n')
                        else:
                            config_file.write(key + '=' + '"' + value.__str__() + '"\n')
                    config_file.close()
                print("Config saved.")
                return "Config saved."
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            errno, strerror = ex.args
            print("Error %s: %s" % (errno, strerror))
            return "Error: " + strerror


