"""
    An IRC Bot - What else could it be?

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
from anircbot.util import safe_path, log_file_name
from datetime import datetime


class Logging(dict):
    """
    The logger class, why not use a dict?
    """
    def __init__(self, iterable, file_name=None, file_extension=None):
        super(dict)
        this_dict = {}
        if iterable:
            if type(iterable) is dict:
                for key, value in iterable.items():
                    this_dict[key] = value
        dict.__init__(this_dict)
        self.now = datetime.now()
        if file_name:
            self.file_name = file_name
        else:
            self.file_name = "anircbot"
        if file_extension:
            self.file_extension = file_extension
        else:
            self.file_extension = ".log"
        self.current_file = log_file_name(self.file_name, self.file_extension)
        if os.path.isfile(self.current_file):
            self.from_file(self.file_name, self.file_extension)

    def from_file(self, file_name="anircbot", file_extension='.log'):
        try:
            file_path = log_file_name(file_name, file_extension)
            if safe_path(file_path):
                with open(file_path, 'r') as log_file:
                    log_string = log_file.read()
                    lines = log_string.split('\n')
                    for line in lines:
                        if line:
                            line_split = line.split('=')
                            if len(line_split):
                                self[line_split[0]] = ast.literal_eval(line_split[1])
                    log_file.close()
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            if len(ex.args):
                errno, strerror = ex.args
                print("Error %s: %s" % (errno, strerror))
            else:
                print("Error: %s" % ex.message)
        return "Success"

    def to_file(self, file_path=None):
        try:
            if file_path is None:
                file_path = self.current_file
            if safe_path(file_path):
                with open(file_path, 'a') as log_file:
                    log_file.seek(0)
                    log_file.truncate()
                    for key, value in self.items():
                        log_file.write(key + '=' + value.__str__() + '\n')
                    log_file.close()
                print("Log saved.")
                return "Log saved."
            else:
                print("Unsafe path not allowed.")
                return "Unsafe path not allowed."
        except Exception as ex:
            if len(ex.args):
                errno, strerror = ex.args
                print("Error %s: %s" % (errno, strerror))
            else:
                print("Error: %s" % ex.message)
            return "Error: " + strerror

    def write_log_entry(self, user, channel, message):
        now = datetime.now()
        if self.now.day != now.day:
            self.to_file(self.current_file)
        self.now = now
        self.current_file = log_file_name(self.file_name, self.file_extension)
        if self.get(channel):
            if self[channel].get(user):
                self[channel][user][str(now)] = message
            else:
                self[channel][user] = {str(now): message}
        else:
            self[channel] = {user: {str(now): message}}
