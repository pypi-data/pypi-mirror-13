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


def add(bot, channel="", user="", text=""):
    if len(text) > 0:
        if not bot.users.get(text):
            new_user = {'op': False, 'added_by': user}
            bot.users[text] = new_user
            bot.send_message('NOTICE %s :%s added to the bot.' % (channel, text))
        else:
            bot.send_message('NOTICE %s :%s already added to the bot.' % (channel, text))
    else:
        bot.send_message('NOTICE %s :You need to specify a user' % channel)
        bot.send_message('NOTICE %s :Syntax: ~add user_name' % channel)


def ban(bot, channel="", user="", text=""):
    text = text.split()
    if len(text) > 1:
        bot.send_message('PRIVMSG ChanServ :AKICK %s ADD %s !P  %s ' % (channel, text[1],
                                                                        ' '.join(text[2:])))
        bot.akick_sent = True
        bot.akick_channel = channel
        bot.akick_user = text[1]
    else:
        bot.send_message('NOTICE %s :You need to specify a user' % channel)
        bot.send_message('NOTICE %s :Syntax: ~ban user_name reason' % channel)


def hello(bot, channel="", user="", text=""):
    bot.send_message('PRIVMSG %s :yo' % channel)


def help(bot, channel="", user="", text=""):
    split_user = user.split('!')
    bot.send_message('NOTICE %s :Accessible Commands:' % split_user[0])
    bot.send_message('NOTICE %s :~hello - Sends a friendly greeting' % split_user[0])
    bot.send_message('NOTICE %s :~help  - Displays this menu' % split_user[0])


def info(bot, channel="", user="", text=""):
    if bot.users_seen.get(text):
        user_seen = bot.users_seen[text]
        message_string = "NOTICE %s :" % channel
        message_string += text + " was first seen at " + str(user_seen['first_seen']) + \
        " and last seen at " + str(user_seen['last_seen']) + " in " + user_seen['last_channel'] + \
        " they have sent " + str(user_seen['message_count']) + " total messages in " + \
        str(len(user_seen['channels'])) + " different channels "
        user_in_this_channel = user_seen['channels'].get(channel)
        if user_in_this_channel:
            message_string += str(user_seen['channels'][channel]['message_count'])
        else:
            message_string += "none"
        message_string += " of those messages were in this channel."

        bot.send_message(message_string)
        message_string = "NOTICE %s :" % channel
        if user_in_this_channel:
            message_string += text + " was first seen in this channel at " + \
            str(user_seen['channels'][channel]['first_seen']) + " and last seen at " + \
            str(user_seen['channels'][channel]['last_seen']) + " the first host mask seen was " + \
            user_seen['hosts'][0] + " and the last was " + user_seen['hosts'][-1] + \
            " the first nick and host was " + user_seen['full_first_username']
        else:
            message_string += text + " has never been seen in this channel" + \
            ", the first host mask seen was " + \
            user_seen['hosts'][0] + " and the last was " + user_seen['hosts'][-1] + \
            " the first nick and host was " + user_seen['full_first_username']
        bot.send_message(message_string)
    else:
        bot.send_message('NOTICE %s :You need to specify a user or user not found' % channel)
        bot.send_message('NOTICE %s :Syntax: ~user nickname' % channel)


def invite(bot, channel="", user="", text=""):
    if len(text) > 0:
        bot.send_message('MODE %s +I %s' % (channel, text))
    else:
        bot.send_message('NOTICE %s :You need to specify a user' % channel)
        bot.send_message('NOTICE %s :Syntax: ~invite user_name' % channel)


def join(bot, channel="", user="", text=""):
    if len(text) > 1:
        bot.send_message('JOIN %s' % text)
    else:
        bot.send_message('NOTICE %s :You need to specify a channel' % channel)
        bot.send_message('NOTICE %s :Syntax: ~join channel_name' % channel)


def kick(bot, channel="", user="", text=""):
    text = text.split()
    user = text[0]
    user_split = user.split('!')
    ident_host_split = user_split[1].split('@')
    user_mask = user_split[0] + '!*@' + ident_host_split[1]
    if len(text) > 1:
        bot.send_message('PRIVMSG ChanServ :AKICK %s ADD %s !T %s  %s ' % (channel, user_mask, text[1],
                                                                           ' '.join(text[2:])))
        bot.akick_sent = True
        bot.akick_channel = channel
        bot.akick_user = user_split[0]
    else:
        bot.send_message('NOTICE %s :You need to specify a user and time' % channel)
        bot.send_message('NOTICE %s :Syntax: ~kick user_name time reason' % channel)


def leave(bot, channel="", user="", text=""):
    if len(text) > 0:
        bot.send_message('PART %s' % text)
    else:
        bot.send_message('NOTICE %s :You need to specify a channel' % channel)
        bot.send_message('NOTICE %s :Syntax: ~join channel_name' % channel)


def load(bot, channel="", user="", text=""):
    text = text.split(' ')
    if len(text) > 0:
        result = bot.config.from_file(text[0])
        bot.send_message('NOTICE %s :%s' % (channel, result))
    else:
        result = bot.config.from_file()
        bot.send_message('NOTICE %s :%s' % (channel, result))
    if result == 'Success':
        bot.users = bot.config['USERS']
        if bot.current_nick != bot.config['NICKNAME']:
            bot.send_message('NICK %s' % bot.config['NICKNAME'])
            bot.current_nick = bot.config['NICKNAME']
            bot.send_message('USER %s localhost %s :"%s"' % (bot.config['NICKNAME'], bot.config['HOST'],
                                                             bot.config['REAL_NAME']))
            bot.send_message('PRIVMSG NickServ :IDENTIFY %s' % bot.config['PASSWORD'])
            bot.send_message('NOTICE %s :%s' % (channel, 'Nickname updated and identified.'))


def nick(bot, channel="", user="", text=""):
    if len(text) > 0:
        bot.send_message('NICK %s' % text)
    else:
        bot.send_message('NOTICE %s :You need to specify a nickname' % channel)
        bot.send_message('NOTICE %s :Syntax: ~nick new_nickname' % channel)


def opup(bot, channel="", user="", text=""):
    bot.send_message('PRIVMSG ChanServ :op %s' % channel)


def op_help(bot, channel="", user="", text=""):
    split_user = user.split('!')
    bot.send_message('NOTICE %s :Accessible Commands:' % split_user[0])
    bot.send_message('NOTICE %s :~add            - Adds a user to the bot' % split_user[0])
    bot.send_message('NOTICE %s :~ban            - Bans a user from the channel' % split_user[0])
    bot.send_message('NOTICE %s :~hello          - Sends a friendly greeting' % split_user[0])
    bot.send_message('NOTICE %s :~help           - Displays this menu' % split_user[0])
    bot.send_message('NOTICE %s :~info           - Displays info for a nickname' % split_user[0])
    bot.send_message('NOTICE %s :~join           - Join a channel' % split_user[0])
    bot.send_message('NOTICE %s :~kick           - Kickbans a user from channel temporarily' % split_user[0])
    bot.send_message('NOTICE %s :~leave          - Leave a channel' % split_user[0])
    bot.send_message('NOTICE %s :~load           - Loads config from file' % split_user[0])
    bot.send_message('NOTICE %s :~nick           - Changes nickname' % split_user[0])
    bot.send_message('NOTICE %s :~opup           - Bot attempts to gain op in channel' % split_user[0])
    bot.send_message('NOTICE %s :~remove         - Deletes a user from the bot' % split_user[0])
    bot.send_message('NOTICE %s :~save           - Saves current config to file' % split_user[0])
    bot.send_message('NOTICE %s :~say            - Sends a message to the current channel' % split_user[0])
    bot.send_message('NOTICE %s :~say_in         - Sends a message to a specific channel' % split_user[0])
    bot.send_message('NOTICE %s :~user           - Display detailed information about a user' % split_user[0])
    bot.send_message('NOTICE %s :~users          - Displays list of users added to bot' % split_user[0])
    bot.send_message('NOTICE %s :~seen           - Displays list of nicknames seen' % split_user[0])


def remove(bot, channel="", user="", text=""):
    if len(text) > 0:
        if bot.users.get(text):
            bot.users.pop(text, None)
            bot.send_message('NOTICE %s :%s removed from the bot.' % (channel, text))
        else:
            bot.send_message('NOTICE %s :%s is not a user on the bot.' % (channel, text))
    else:
        bot.send_message('NOTICE %s :You need to specify a user' % channel)
        bot.send_message('NOTICE %s :Syntax: ~remove user_name' % channel)


def save(bot, channel="", user="", text=""):
    text = text.split(' ')
    if len(text) > 0:
        result = bot.config.to_file(text[0])
        bot.send_message('NOTICE %s :%s' % (channel, result))
    else:
        result = bot.config.to_file()
        bot.send_message('NOTICE %s :%s' % (channel, result))


def say(bot, channel="", user="", text=""):
    if len(text) > 1:
        bot.send_message('NOTICE %s :%s' % (channel, text))
    else:
        bot.send_message('NOTICE %s :You need to specify a message' % channel)
        bot.send_message('NOTICE %s :Syntax: ~say message' % channel)


def say_in(bot, channel="", user="", text=""):
    text = text.split(' ')
    if len(text) > 1:
        bot.send_message('NOTICE %s :%s' % (text[0], ' '.join(text[1:])))
    else:
        bot.send_message('NOTICE %s :You need to specify a channel and message' % channel)
        bot.send_message('NOTICE %s :Syntax: ~say_in channel_name message' % channel)


def whisper(bot, channel="", user="", text=""):
    text = text.split(' ')
    if len(text) > 1:
        bot.send_message('PRIVMSG %s :%s' % (text[0], ' '.join(text[1:])))
    else:
        bot.send_message('PRIVMSG %s :You need to specify a channel and message' % channel)
        bot.send_message('PRIVMSG %s :Syntax: ~say_in channel_name message' % channel)


def seen(bot, channel="", user="", text=""):
    users_string = "I've seen "
    first_user = True
    for key, value in bot.users_seen.items():
        if first_user:
            users_string += key
            first_user = False
        else:
            users_string += ', %s' % key
    if len(users_string) > 500:
        while len(users_string) > 500:
            message_string = users_string[:500]
            bot.send_message('NOTICE %s :%s' % (channel, message_string))
            users_string = users_string[500:]
        if users_string > 0:
            bot.send_message('NOTICE %s :%s' % (channel, users_string))
    else:
        bot.send_message('NOTICE %s :%s' % (channel, users_string))


def user_help(bot, channel="", user="", text=""):
    split_user = user.split('!')
    bot.send_message('NOTICE %s :Accessible Commands:' % split_user[0])
    bot.send_message('NOTICE %s :~hello       - Sends a friendly greeting' % split_user[0])
    bot.send_message('NOTICE %s :~help        - Displays this menu' % split_user[0])
    bot.send_message('NOTICE %s :~info        - Displays info for a nickname' % split_user[0])
    bot.send_message('NOTICE %s :~seen        - Displays list of users seen' % split_user[0])


def users(bot, channel="", user="", text=""):
    bot.send_message('NOTICE %s :User Access' % channel)
    for user, value in bot.users.items():
        bot.send_message('NOTICE %s :%s - Op: %s ' % (channel, user, str(value['op'])))

