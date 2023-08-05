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
from anircbot.event.commands import *
from anircbot.event.replies import *


def execute_command(bot, command, **args):
    if commands.get(command):
        commands[command](bot, **args)


def input_received(bot, input):
    input_split = input.split()
    if input_split[0] == 'PING':
        reply = 'PING'
    elif input_split[0] == 'ERROR':
        reply = 'ERROR'
    elif input_split[0] == 'AUTHENTICATE':
        reply = 'AUTHENTICATE'
    else:
        reply = input_split[1]
    if replies.get(reply):
        replies[reply](bot, input)


commands = {
    'add': add,
    'ban': ban,
    'help': help,
    'hello': hello,
    'info': info,
    'invite': invite,
    'join': join,
    'kick': kick,
    'leave': leave,
    'load': load,
    'nick': nick,
    'opup': opup,
    'op_help': op_help,
    'remove': remove,
    'save': save,
    'say': say,
    'say_in': say_in,
    'seen': seen,
    'user_help': user_help,
    'users': users,
    'whisper': whisper
}

replies = {
    '001': reply_001,
    '002': reply_002,
    '003': reply_003,
    '004': reply_004,
    '005': reply_005,
    '250': reply_250,
    '251': reply_251,
    '252': reply_252,
    '253': reply_253,
    '254': reply_254,
    '255': reply_255,
    '265': reply_265,
    '266': reply_266,
    '372': reply_372,
    '375': reply_375,
    '376': reply_376,
    '396': reply_396,
    '900': reply_900,
    '903': reply_903,
    'AUTHENTICATE': reply_authenticate,
    'CAP': reply_cap,
    'ERROR': reply_error,
    'INVITE': reply_invite,
    'JOIN': reply_join,
    'MODE': reply_mode,
    'NOTICE': reply_notice,
    'PART': reply_part,
    'PING': reply_ping,
    'PRIVMSG': reply_privmsg,
    'QUIT': reply_quit
}
