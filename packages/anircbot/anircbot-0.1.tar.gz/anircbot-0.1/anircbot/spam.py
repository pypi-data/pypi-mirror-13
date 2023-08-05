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
from collections import Counter
from datetime import datetime, timedelta


def spam_check(bot, user, channel, message):
    is_spam = False
    if user != "ChanServ!ChanServ@services." and user != "NickServ!NickServ@services.":
        user_split = user.split('!')
        ident_host_split = user_split[1].split('@')
        last_message = ("", datetime.now())
        same_message = False
        same_message_count = 0
        if bot.users_seen.get(user_split[0]):
            for message in bot.users_seen[user_split[0]]['last_messages']:

                if last_message[0] != "":
                    if message[0] == last_message[0]:
                        same_message = True
                    if message[0] != last_message[0]:
                        same_message = False
                        same_message_count = 0
                    if message[1] - last_message[1] < timedelta(milliseconds=500):
                        is_spam = True
                last_message = message
                if same_message:
                    same_message_count += 1
                    if same_message_count > 2:
                        is_spam = True
        last_message = ("", datetime.now())
        same_message_count = 0
        if bot.hosts_seen.get(ident_host_split[1]):
            for message in bot.hosts_seen[ident_host_split[1]]['last_messages']:
                if last_message[0] != "":
                    if message[0] == last_message[0]:
                        same_message = True
                    if message[0] != last_message[0]:
                        same_message = False
                        same_message_count = 0
                    if message[1] - last_message[1] < timedelta(milliseconds=500):
                        is_spam = True
                last_message = message
                if same_message:
                    same_message_count += 1
                    if same_message_count > 2:
                        is_spam = True

        if len(message) == 500:
            is_spam = True
        if '`' == bot.config["COMMAND_TRIGGER"] and message[0] != bot.config["COMMAND_TRIGGER"]:
            if '`' in message:
                is_spam = True

    return is_spam
