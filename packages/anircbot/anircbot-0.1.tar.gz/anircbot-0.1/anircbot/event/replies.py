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
import base64
from datetime import datetime


def reply_cap(bot, data):
    data_split = data.split()
    if not bot.sasl_req_sent and 'sasl' in data_split:
        bot.send_message('CAP REQ :sasl')
        bot.sasl_req_sent = True
    if not bot.sent_nick:
        bot.prompt = data_split[0]
        bot.send_message('NICK ' + bot.config['NICKNAME'])
        bot.current_nick = bot.config['NICKNAME']
        bot.sent_nick = True
    if not bot.sent_user:
        bot.send_message('USER %s localhost %s :"%s"' % (bot.config['NICKNAME'], bot.config['HOST'],
                                                         bot.config['REAL_NAME']))
        bot.sent_user = True
    if data_split[3] == 'ACK' and not bot.sasl_authenticate_sent:
        bot.send_message('AUTHENTICATE PLAIN')
        bot.sasl_authenticate_sent = True


def reply_authenticate(bot, data):
    if not bot.sasl_auth_string_sent:
        auth_string = base64.b64encode('\0'.join((bot.config['NICKNAME'],
                                                  bot.config['NICKNAME'],
                                                  bot.config['PASSWORD'])))
        bot.send_message('AUTHENTICATE %s' % auth_string)
        bot.sasl_auth_string_sent = True


def reply_notice(bot, data):
    data_split = data.split()
    print("Received Notice: " + ' '.join(data_split[2:]))
    if bot.config['USE_SASL']:
        if not bot.sasl_ls_sent:
            bot.send_message('CAP LS')
            bot.sasl_ls_sent = True
            return
    elif not bot.config['USE_SASL']:
        if not bot.sent_nick:
            bot.prompt = data_split[0]
            bot.send_message('NICK ' + bot.config['NICKNAME'])
            bot.current_nick = bot.config['NICKNAME']
            bot.sent_nick = True
        if not bot.sent_user:
            bot.send_message('USER %s localhost %s :"%s"' % (bot.config['NICKNAME'], bot.config['HOST'],
                                                             bot.config['REAL_NAME']))
            bot.sent_user = True
        if not bot.sent_identify:
            bot.send_message('PRIVMSG NickServ :IDENTIFY %s' % bot.config['PASSWORD'])
            bot.sent_identify = True
        if bot.akick_sent:
            akick_notify = False
            if 'authorized' in ' '.join(data_split[3:]):
                bot.send_message('PRIVMSG %s :I don\'t have permission to AKICK, please set +rf and op me.' %
                                  bot.akick_channel)
                akick_notify = True
            if 'successfully' in ' '.join(data_split[3:]):
                bot.send_message('PRIVMSG %s :RIP %s' % (bot.akick_channel, bot.akick_user))
                akick_notify = True
            if akick_notify:
                bot.akick_sent = False
                bot.akick_channel = ""
                bot.akick_user = ""
        if data_split[0] != bot.prompt:
            user = data_split[0][1:]
            user_split = user.split('!')
            ident_host_split = user_split[1].split('@')
            channel = data_split[2]
            message = ' '.join([data_split[3][1:]] + data_split[4:])
            if bot.config['DEBUG']:
                print('User: ' + user_split[0] + ' Said: ' +
                      message + ' In: ' + channel)
            if bot.config['LOGGING']:
                try:
                    bot.logger.write_log_entry(user, channel, message)
                except Exception as ex:
                    if bot.python3:
                        errno, stderro = ex.args
                        print("Error %s: %s" % (errno, stderro))
                    else:
                        print("Error: %s" % ex.message)
            if not bot.hosts_seen.get(ident_host_split[1]):
                bot.hosts_seen[ident_host_split[1]] = {'channels': {
                                                            channel: {
                                                                'message_count': 1,
                                                                'first_seen': datetime.now(),
                                                                'last_seen': datetime.now(),
                                                                'first_user': user_split[0],
                                                                'last_user': user_split[0],

                                                            },
                                                        },
                                                       'message_count': 1,
                                                       'last_messages': [([' '.join([data_split[3][1:]] + data_split[4:])], datetime.now())]
                                                       }
            if not bot.users_seen.get(user_split[0]):
                bot.users_seen[user_split[0]] = {'hosts': [ident_host_split[1]],
                                                 'full_first_username': user,
                                                 'ident': [ident_host_split[0]],
                                                 'first_seen': datetime.now(), 'last_seen': datetime.now(),
                                                 'message_count': 1,
                                                 'channels': {
                                                              channel: {'message_count': 1,
                                                                        'first_seen': datetime.now(),
                                                                        'last_seen': datetime.now(),
                                                                        'first_host': ident_host_split[1],
                                                                        'last_host': ident_host_split[1]}},
                                                 'last_channel': channel,
                                                 'last_messages': [([' '.join([data_split[3][1:]] + data_split[4:])], datetime.now())]
                                                 }
            else:
                if len(bot.users_seen[user_split[0]]['last_messages']) > 10:
                    bot.users_seen[user_split[0]]['last_messages'].pop(0)
                if len(bot.hosts_seen[ident_host_split[1]]['last_messages']) > 10:
                    bot.hosts_seen[ident_host_split[1]]['last_messages'].pop(0)
                bot.hosts_seen[ident_host_split[1]]['last_messages'].append((' '.join([data_split[3][1:]] + data_split[4:]), datetime.now()))
                bot.hosts_seen[ident_host_split[1]]['message_count'] += 1
                bot.users_seen[user_split[0]]['last_messages'].append((' '.join([data_split[3][1:]] + data_split[4:]),
                                                                       datetime.now()))
                bot.users_seen[user_split[0]]['message_count'] += 1
                bot.users_seen[user_split[0]]['last_channel'] = channel
                if ident_host_split[1] not in bot.users_seen[user_split[0]]['hosts']:
                    bot.users_seen[user_split[0]]['hosts'].append(ident_host_split[1])
                if ident_host_split[0] not in bot.users_seen[user_split[0]]['ident']:
                    bot.users_seen[user_split[0]]['ident'].append(ident_host_split[0])
                if bot.users_seen[user_split[0]]['channels'].get(channel):
                    bot.users_seen[user_split[0]]['channels'][channel]['message_count'] += 1
                    bot.users_seen[user_split[0]]['channels'][channel]['last_seen'] = datetime.now()
                else:
                    bot.users_seen[user_split[0]]['channels'][channel] = {'message_count': 1,
                                                                          'first_seen': datetime.now(),
                                                                          'last_seen': datetime.now(),
                                                                          'first_host': ident_host_split[1],
                                                                          'last_host': ident_host_split[1]}
            bot.notice_spam(data)
            
            
def reply_001(bot, data):
    pass


def reply_002(bot, data):
    pass  # Host information, we use 004 due to easier parsing


def reply_003(bot, data):
    data_split = data.split()
    bot.server_created = ' '.join([data_split[3][1:]] + data_split[4:])


def reply_004(bot, data):
    data_split = data.split()
    bot.actual_host = data_split[3]
    bot.server_software = data_split[4]


def reply_005(bot, data):
    data_split = data.split()
    bot.server_features += ' '.join(data_split[3:-5])  # -5 removes :are supported by this server


def reply_250(bot, data):
    data_split = data.split()
    bot.server_highest_client_count = data_split[6]
    bot.server_highest_client_connections_count = data_split[9][1:]


def reply_251(bot, data):
    data_split = data.split()
    bot.server_users = data_split[5]
    bot.server_invisible_users = data_split[8]
    bot.servers = data_split[11]


def reply_252(bot, data):
    data_split = data.split()
    bot.server_operators_online = data_split[3]


def reply_253(bot, data):
    data_split = data.split()
    bot.server_unknown_connections = data_split[3]


def reply_254(bot, data):
    data_split = data.split()
    bot.server_channels_formed = data_split[3]


def reply_255(bot, data):
    pass  # 265 gives us move information, so we use that instead


def reply_265(bot, data):
    data_split = data.split()
    bot.server_local_users = data_split[3]
    bot.server_local_max_users = data_split[4]


def reply_266(bot, data):
    data_split = data.split()
    bot.server_global_users = data_split[3]
    bot.server_global_max_users = data_split[4]


def reply_372(bot, data):
    data_split = data.split()
    bot.server_motd += ' '.join([data_split[3][1:]] + data_split[4:])


def reply_375(bot, data):
    bot.server_motd = ""  # better clear this just in case


def reply_376(bot, data):
    pass  # end of server motd nothing needs to be done here


def reply_396(bot, data):
    for channel in bot.config['DEFAULT_CHANNELS']:
        bot.send_message('JOIN %s' % channel)
        bot.send_message('PRIVMSG ChanServ :op %s' % channel)


def reply_join(bot, data):
    pass  # we joined a channel or someone joined our channel
    #TODO: store in a file or something


def reply_mode(bot, data):
    pass  # mode changed
    #TODO: do something?


def reply_part(bot, data):
    pass  # we left a channel or someone left our channel
    #TODO: store in a file or something


def reply_quit(bot, data):
    pass  # we quit or someone else quit
    #TODO: store in a file or something


def reply_invite(bot, data):
    pass  # we invited someone or got invited to a channel
    #TODO: store in a file or something


def reply_privmsg(bot, data):
    data_split = data.split()
    user = data_split[0][1:]
    user_split = user.split('!')
    ident_host_split = user_split[1].split('@')
    channel = data_split[2]
    message = ' '.join([data_split[3][1:]] + data_split[4:])
    if bot.config['DEBUG']:
        print('User: ' + user_split[0] + ' Said: ' +
              message + ' In: ' + channel)
    if bot.config['LOGGING']:
        bot.logger.write_log_entry(user, channel, message)
    if not bot.hosts_seen.get(ident_host_split[1]):
        bot.hosts_seen[ident_host_split[1]] = {'channels': {
                                                    channel: {
                                                        'message_count': 1,
                                                        'first_seen': datetime.now(),
                                                        'last_seen': datetime.now(),
                                                        'first_user': user_split[0],
                                                        'last_user': user_split[0],

                                                    },
                                                },
                                               'message_count': 1,
                                               'last_messages': [([' '.join([data_split[3][1:]] + data_split[4:])], datetime.now())]
                                               }
    if not bot.users_seen.get(user_split[0]):
        bot.users_seen[user_split[0]] = {'hosts': [ident_host_split[1]],
                                         'full_first_username': user,
                                         'ident': [ident_host_split[0]],
                                         'first_seen': datetime.now(), 'last_seen': datetime.now(),
                                         'message_count': 1,
                                         'channels': {
                                                      channel: {'message_count': 1,
                                                                'first_seen': datetime.now(),
                                                                'last_seen': datetime.now(),
                                                                'first_host': ident_host_split[1],
                                                                'last_host': ident_host_split[1]}},
                                         'last_channel': channel,
                                         'last_messages': [(' '.join([data_split[3][1:]] + data_split[4:]), datetime.now())]
                                         }
    else:
        if len(bot.users_seen[user_split[0]]['last_messages']) > 10:
            bot.users_seen[user_split[0]]['last_messages'].pop(0)
        bot.users_seen[user_split[0]]['last_messages'].append((' '.join([data_split[3][1:]] + data_split[4:]),
                                                                       datetime.now()))
        bot.users_seen[user_split[0]]['message_count'] += 1
        bot.users_seen[user_split[0]]['last_channel'] = channel
        if len(bot.hosts_seen[ident_host_split[1]]['last_messages']) > 10:
            bot.hosts_seen[ident_host_split[1]]['last_messages'].pop(0)
        bot.hosts_seen[ident_host_split[1]]['last_messages'].append((' '.join([data_split[3][1:]] + data_split[4:]),
                                                                     datetime.now()))
        bot.hosts_seen[ident_host_split[1]]['message_count'] += 1
        if ident_host_split[1] not in bot.users_seen[user_split[0]]['hosts']:
            bot.users_seen[user_split[0]]['hosts'].append(ident_host_split[1])
        if ident_host_split[0] not in bot.users_seen[user_split[0]]['ident']:
            bot.users_seen[user_split[0]]['ident'].append(ident_host_split[0])
        if bot.users_seen[user_split[0]]['channels'].get(channel):
            bot.users_seen[user_split[0]]['channels'][channel]['message_count'] += 1
            bot.users_seen[user_split[0]]['channels'][channel]['last_seen'] = datetime.now()
        else:
            bot.users_seen[user_split[0]]['channels'][channel] = {'message_count': 1,
                                                                  'first_seen': datetime.now(),
                                                                  'last_seen': datetime.now(),
                                                                  'first_host': ident_host_split[1],
                                                                  'last_host': ident_host_split[1]}
    bot.parse_chat(data_split[0][1:], [data_split[3][1:]] + data_split[4:], data_split[2])


def reply_900(bot, data):
    """
        Logged in identity
    """
    pass


def reply_903(bot, data):
    """
        Authentication Reply
    """
    data_split = data.split()
    if data_split[-1] == 'successful':
        bot.sasl_authentication_success = True
        bot.send_message('CAP END')
    else:
        bot.sasl_authentication_success = False


def reply_ping(bot, data):
    data_split = data.split()
    bot.send_message('PONG ' + data_split[1])


def reply_error(bot, data):
    data_split = data.split()
    if ' '.join(data_split[-3:]) == "(SASL access only)":
        if bot.config['DEBUG']:
            print("SASL required")
        bot.sasl_required = True
    else:
        if bot.config['DEBUG']:
            print("Not Supported: %s" % data)
