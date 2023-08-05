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
import sys
import socket
import time
import variance
from datetime import datetime
from anircbot.event import execute_command, input_received
from anircbot.logging import Logging
from anircbot.spam import spam_check
from anircbot.util import CRLF


class AnIRCBot:
    """
        The class yo.
    """

    def __init__(self, nickname='', password='', host='', port=6667, buffer_size=4096,
                 email_address='', real_name='', default_channels=[],
                 users={'bschumacher!~bschumach@unaffiliated/bschumacher': {'op': True},}, debug=False, logging=False,
                 use_sasl=False):
        self.config = variance.Variance(default_config)
        self.logger = None
        if nickname != '':
            self.config['NICKNAME'] = nickname
        if password != '':
            self.config['PASSWORD'] = password
        if host != '':
            self.config['HOST'] = host
        if port != 6667:
            self.config['PORT'] = port
        if buffer_size != 4096:
            self.config['BUFFER_SIZE'] = buffer_size
        if email_address != '':
            self.config['EMAIL_ADDRESS'] = email_address
        if real_name != '':
            self.config['REAL_NAME'] = real_name
        if len(default_channels) > 0 and default_channels is list:
            self.config['DEFAULT_CHANNELS'] = default_channels
        if len(users) > 0 and users is dict:
            self.config['USERS'] = users
        if debug:
            self.config['DEBUG'] = True
        if logging:
            self.config['LOGGING'] = True
        if use_sasl:
            self.config['USE_SASL'] = True
        self.connection = None
        self.running = False
        self.actual_host = None
        self.server_software = None
        self.server_created = None
        self.server_features = ""
        self.server_users = 0
        self.server_invisible_users = 0
        self.servers = 0
        self.server_operators_online = 0
        self.server_unknown_connections = 0
        self.server_channels_formed = 0
        self.server_local_users = 0
        self.server_local_max_users = 0
        self.server_global_users = 0
        self.server_global_max_users = 0
        self.server_highest_client_count = 0
        self.server_highest_client_connections_count = 0
        self.server_motd = ""
        self.channels = []
        self.users = users
        self.users_seen = {}
        self.hosts_seen = {}
        self.spammers = []
        self.pending_spam = []
        self.current_nick = ""
        self.sent_nick = False
        self.sent_user = False
        self.sent_identify = False
        self.prompt = ""
        self.akick_sent = False
        self.akick_channel = ""
        self.akick_user = ""
        self.last_command_sent = None
        self.op_commands = ['add', 'ban', 'help', 'invite', 'join', 'kick', 'leave', 'load',
                            'nick', 'opup', 'remove', 'save', 'say', 'say_in', 'users', 'whisper']
        self.user_commands = ['hello', 'help', 'seen', 'info']
        self.public_commands = ['hello', 'help']
        self.sasl_required = False
        self.sasl_ls_sent = False
        self.sasl_req_sent = False
        self.sasl_end_sent = False
        self.sasl_authenticate_sent = False
        self.sasl_auth_string_sent = False
        self.sasl_authentication_success = False
        self.python3 = False
        if sys.version_info >= (3, 0):
            self.python3 = True

    def connect(self):
        if self.config['LOGGING']:
            self.logger = Logging({})
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect((self.config['HOST'], int(self.config['PORT'])))
        except Exception as ex:
            errno, strerror = ex.args
            print("Error %s: %s" % (errno, strerror))
            print("Connection Failed!", 'utf-8')
            sys.exit()
        self.run()

    def run(self):
        self.running = True
        if self.python3:
            data = bytes()
        else:
            data = ""
        while self.running:
            try:
                data += self.connection.recv(self.config['BUFFER_SIZE'])
            except KeyboardInterrupt as ex:
                if self.python3:
                    errno, strerror = ex.args
                    print("Error %s: %s" % (errno, strerror))
                else:
                    print("Error: Halted by user")
                if self.config['LOGGING']:
                    self.logger.to_file()
                sys.exit()
            if self.python3:
                if len(data) > 0:
                    print(data.decode())
                    data_string = data.decode()
                    while data_string.find(CRLF) != -1:
                        index = data_string.find(CRLF)
                        data_in = data_string[:index]
                        self.parse_input(data_in)
                        data_string = data_string[(index + len(CRLF)):]
                    data = bytes(data_string, 'utf-8')
                else:
                    if self.sasl_required and not self.sasl_ls_sent:
                        self.sent_nick = False
                        self.sent_identify = False
                        self.sent_user = False
                        self.config['USE_SASL'] = True
                        self.connect()
                    print("Connection Closed!")
                    if self.config['LOGGING']:
                        self.logger.to_file()
                    sys.exit()
            else:
                if data:
                    while data.find(CRLF) != -1:
                        index = data.find(CRLF)
                        data_in = data[:index]
                        self.parse_input(data_in)
                        data = data[(index + len(CRLF)):]
                else:
                    if self.sasl_required and not self.sasl_ls_sent:
                        self.sent_nick = False
                        self.sent_identify = False
                        self.sent_user = False
                        self.config['USE_SASL'] = True
                        self.connect()
                    print("Connection Closed!")
                    if self.config['LOGGING']:
                        self.logger.to_file()
                    sys.exit()

    def parse_input(self, data):
        if data:
            if self.config['DEBUG']:
                print("Received: " + data)
            input_received(self, data)
        else:
            if self.config['DEBUG']:
                print("No data received")

    def parse_chat(self, user, message, channel):
        if len(message[0]):
            if message[0][0] == self.config['COMMAND_TRIGGER']:
                command = message[0][1:]
                if user in self.users:
                    if command in self.op_commands and self.users[user]['op']:
                        if command == 'help':
                            command = 'op_help'
                        execute_command(self, command, channel=channel, user=user, text=' '.join(message[1:]))
                        return
                    elif command in self.user_commands:
                        if command == 'help':
                            command = 'user_help'
                        execute_command(self, command, channel=channel, user=user, text=' '.join(message[1:]))
                        return
                else:
                    if command in self.public_commands:
                        execute_command(self, command, channel=channel, user=user, text=' '.join(message[1:]))

            if user not in self.users:
                if spam_check(self, user, channel, message):
                    if user not in self.pending_spam:
                        text = user
                        text += " %s" % str(self.config['SPAM_KICK_TIME'])
                        text += " Spamming is not allowed in here."
                        execute_command(self, 'kick', channel=channel, user=user, text=text)
                        self.pending_spam.append(user)

    def notice_spam(self, data):
        data_split = data.split()
        if data_split[0] is not self.prompt:
            user = data_split[0][1:]
            channel = data_split[2]
            message = ' '.join([data_split[3][1:]] + data_split[4:])
            if spam_check(self, user, data, message):
                if user not in self.pending_spam:
                    self.pending_spam.append(user)
                    text = data_split[0][1:]
                    text += " %s" % str(self.config['SPAM_KICK_TIME'])
                    text += " Spamming is not allowed in here."
                    execute_command(self, 'kick', channel=channel, user=user, text=text)

    def send_message(self, message):
        try:
            message += CRLF
            if self.last_command_sent is None:
                if self.python3:
                    self.connection.send(bytes(message, 'utf-8'))
                else:
                    self.connection.send(message)
                self.last_command_sent = datetime.now()
            else:
                if self.python3:
                    self.connection.send(bytes(message, 'utf-8'))
                else:
                    self.connection.send(message)
                self.last_command_sent = datetime.now()
            time.sleep(0.500)
            if self.config['DEBUG']:
                print("Timedelta: " + str(datetime.now() - self.last_command_sent))
                message = message.replace(CRLF, '')
                print("Sent: " + message)
        except KeyboardInterrupt as ex:
            print("Error: Halted by user")
            sys.exit()
        except Exception as ex:
            if self.python3:
                errno, strerror = ex.args
                print("Error %s: %s" % (errno, strerror))
            else:
                print("Error: %s" % ex.message)


default_config = {
    'NICKNAME': 'change_me',
    'PASSWORD': 'change_me',
    'HOST': 'irc.freenode.net',
    'PORT': 6667,
    'BUFFER_SIZE': 4096,
    'EMAIL_ADDRESS': 'email@change.me',
    'SPAM_KICK_TIME': 5,
    'REAL_NAME': 'Mr. IRC Bot',
    'DEFAULT_CHANNELS': ['#anircbot', ],
    'USERS': {'bschumacher!~bschumach@unaffiliated/bschumacher': {'op': True}, },
    'DEBUG': True,
    'LOGGING': True,
    'BACKEND': 'SQLALCHEMY',
    'BACKEND_URI': 'sqlite:///app.db',
    'COMMAND_TRIGGER': '~',
    'USE_SASL': False
}