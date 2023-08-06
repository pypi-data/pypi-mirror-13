#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

"""
DESCRIPTION: This package is released in the context of Re-WoChat: Workshop on Collecting
             and Generating Resources for Chatbots and Conversational Agents - Development
             and Evaluation (see further details at http://workshop.colips.org/re-wochat/)
             as part of the shared task (http://workshop.colips.org/re-wochat/shared.html).

USAGE: This program can be run from the command line by using: python pyClient.py


OUTPUT: A log file called ZenMaster.log, unless the user specifies another name during
        the initialization. Then, from the ZenMaster.log file the system automatically generates
        a XML file to be submitted to the workshop organizers.  

VERSION: 0.1.6
DATE: Feb/05/2016
AUTHORS: Luis Fernando D'Haro, Rafael E. Banchs
EMAILS: luisdhe@i2r.a-star.edu.sg, rembanchs@i2r.a-star.edu.sg

"""

__version__ = "0.1.6"

# Standard Python Packages
import logging
import os
import sys
import atexit
import random
import string
import time
import argparse
import json
import traceback
from builtins import input

from ConfigParser import SafeConfigParser


# External packages
try:
    from nltk import word_tokenize
except ImportError:
    try:
        import nltk
        nltk.download('punkt')
    except:
        raise ImportError('This program cannot run without NLTK and its tokenizer module.'
                          'use: pip install nltk')
    else:
        from nltk import word_tokenize

# Based on https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/reconnecting/client.py
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from twisted.internet import reactor

# Special programs/scripts
from .chatbot import zenmaster
from .utils import createXMLfromJson


# Global variables
_name_logfile = None
_name_chatbot = None
_name_user = None

# Handling the process to create the XML when the system exits
def on_exit():
    # Function to create the XML at the end of the process
    createXMLfromJson.fntCreateXMLFromLogs(chatbot_name=_name_chatbot,
                                           user_name=_name_user,
                                           logfile_name=_name_logfile)

atexit.register(on_exit)


class pyClientChatbot():

    # A dictionary of greetings to get the user's name
    dictNameGreeting = ['Nice to meet you __USR_NAME__ !', '__USR_NAME__ ... What a nice name.',
                        'I am not sure if we have already met __USR_NAME__, but anyway...',
                        'Great __USR_NAME__,']

    # A dictionary of follow up greetings for the chatbot
    dictStartingGreetings = ['What can I do for you?', 'What do you want to talk about?',
                             'How might I help you?', 'How are you doing today?',
                             'How is it going?', 'What''s up?']

    def __init__(self, args, config_file=None):
        global _name_logfile
        global _name_chatbot

        # Default values
        self.server_info = {
            'server_url': 'ws://localhost:8888/ws_chat',
            'host': 'localhost',
            'port': 8888,
        }

        self.client_info = {
            "id": 'ISBjFetqtkx7x4V2',  # Identifier to access the server
            "max_connections": 1,  # Integer. Indicates how many simultaneous users can handle the chatbot
                             # (WARNING: No implemented yet)
            "image": 'ZenMaster.jpg',  # Image to show to the users
            "name": 'ZenMaster',  # Official name of the chatbot. Must be different
                              # from others available chatbots
            "email": 'admin@admin.com',  # Email of person responsible for the chatbot
            "admin_name": 'admin',  # Name of the person responsible for the chatbot
            "description": 'A wise Zen master',  # A short description of the chatbot
            "log_file": 'ZenMaster.log',
            "human": False,
        }

        if config_file is not None:
            _config_file = config_file
        elif args.config is not None:
            _config_file = args.config

        if _config_file is not None:
            parser = SafeConfigParser()
            parser.read(_config_file)
            if parser.has_section('server_info') is True:
                for name, value in parser.items('server_info'):
                    self.server_info[name] = value

            if parser.has_section('client_info') is True:
                for name, value in parser.items('client_info'):
                    self.client_info[name] = value

        elif len(args) > 0:
            self.client_info['log_file'] = args.log
            self.client_info['name'] = args.name
            self.client_info['id'] = args.id
            self.server_info['server_url'] = 'ws://' + args.host + ':' + args.port + '/ws_chat',
            self.client_info['name'] = args.image
            self.client_info['description'] = args.desc

        self.chatbot = zenmaster.zenmaster()
        self.logger = self.init_logger(self.client_info['log_file'])
        self.chatbot_name = self.client_info['name']
        self.chatbot_id = self.client_info['id']
        self.server_info['host'] = self.server_info['host']
        self.server_info['port'] = int(self.server_info['port'])

        _name_logfile = self.client_info['log_file']
        _name_chatbot = self.chatbot_name


    def init_logger(self, log_file='ZenMaster.log',
                    ch_level=logging.DEBUG,
                    f_level=logging.DEBUG):
        global _name_logfile

        logger = logging.getLogger(__name__)
        logger.handlers = []
        logger.setLevel(logging.DEBUG)  # By default we want everything
        formatter = logging.Formatter('%(asctime)-15s | %(name)s | %(levelname)s | %(message)s')

        # File handler showing only info level
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(f_level)
        f_handler.setFormatter(formatter)
        logger.addHandler(f_handler)

        # Console handler showing debug level
        ch_handler = logging.StreamHandler()
        ch_handler.setLevel(ch_level)
        ch_handler.setFormatter(formatter)
        logger.addHandler(ch_handler)

        _name_logfile = log_file

        return logger

    # Simplistic approach to get the name of the user
    def fntGetUserName(self, txt):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        thelist = ['hi', self.chatbot_name, 'hello', 'okay', 'ok',
                 'my', 'name', 'is', 'they', 'call', 'me', 'i', 'am', "'", 'it', "i'm"]
        words = word_tokenize(txt.lower())
        for pos in [i for i, x in enumerate(words) if x in thelist]:
            words[pos] = ''

        userName = ' '.join(words)
        userName = userName.translate(remove_punctuation_map)  # Remove punctuation
        userName = ' '.join(userName.split())
        return userName.capitalize()

    def findRandomAnswer(self, dictionary, name_replace=''):
        random.seed()
        random_num = random.randint(0, len(dictionary)-1)
        answer = dictionary[random_num]
        if len(name_replace.split()) > 0:
            answer = answer.replace('__USR_NAME__', name_replace)
        return answer

    def start(self, stand_alone=False):
        global _name_user
        if stand_alone is True:
            print ('\n***********    WELCOME to pyZenMaster    ************')
            print ('\nPlease type the word: bye or press ctrl-c to exit\n')
            print('**************************************************\n')
            # Re-initialize the logger so the terminal is only showing the turns (i.e. no logs)
            self.init_logger(ch_level=logging.ERROR)

            # Procedure to introduce the chatbot and get the user's name (required when
            # using the chatbot as stand-alone app. When used as a websocket client
            # there will be previously a login process
            self.logger.info('INIT_CHAT | START')
            self.logger.info('CHATBOT_NAME | %s' % _name_chatbot.capitalize())
            start_time = time.time()
            init_salutation = self.chatbot_name + ': Hello, my name is ' + self.chatbot_name \
                         + '. Please tell me your name.'
            print (init_salutation)
            self.logger.info('MSG_CHATBOT | %s' % init_salutation)
            user_input = input('User: ')
            self.logger.info('MSG_USER | %s' % user_input)
            _name_user = self.fntGetUserName(user_input)
            self.logger.info('USER_NAME | %s' % _name_user)
            end_salutation = self.findRandomAnswer(self.dictNameGreeting, _name_user) \
                             + ' ' + self.findRandomAnswer(self.dictStartingGreetings)
            print(end_salutation)
            self.logger.info('MSG_CHATBOT | %s' % end_salutation)

            # Let's start the dialogue
            while True:
                try:
                    user_input = input('User: ')
                    self.logger.info('MSG_USER | %s' % user_input)
                    chat_answer = self.chatbot.respond(user_input)
                    print(self.chatbot_name + ': ' + chat_answer)
                    self.logger.info('MSG_CHATBOT | %s' % chat_answer)
                    if user_input.lower() == 'bye':
                        self.logger.info("CLOSING | USER - duration: %f",
                                         time.time() - start_time)
                        exit()
                except KeyboardInterrupt:
                    self.logger.info("CLOSING | KEYBOARD - duration: %f",
                                     time.time() - start_time)
                    exit()
                except Exception as e:
                    self.logger.error("ERROR | Unexpected error: %s" % sys.exc_info()[0])
                    self.logger.error('Backtrace', exc_info=True)
                    exit()
        else:
            factory = MyClientFactory(self.server_info['server_url'],
                                      debug=False, chatbot=self.chatbot,
                                      logger=self.logger, client_info=self.client_info)
            reactor.connectTCP(self.server_info['host'], self.server_info['port'], factory)
            reactor.run()

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        self.logger.debug("WS_CONNECTED | {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        self.logger.debug("WS_OPENED | OK")
        self.start_time = time.time()
        msg = {'msgtype': 'info_chat', 'payload': self.client_info}
        self.sendMessage(json.dumps(msg))

    def onMessage(self, message, isBinary):
        try:
            msg = json.loads(message)
            msg['chatbot_id'] = self.client_info['id']
            if msg['msgtype'] == 'join':
                self.logger.info('INIT_CHAT | START')
                self.start_time = time.time()
                _name_user = msg['name']
                self.logger.info('USER_NAME | %s' % _name_user.capitalize())
            elif msg['msgtype'] == 'user_turn':  # Answer using the engine
                msg['msgtype'] = 'chat_answer'
                payload_user = msg['payload']
                self.logger.info("MSG_WS_USER | %s" % (msg))

                msg['payload'] = {0: self.chatbot.respond(payload_user)}
                msg['nbest_size'] = 1  # Only one answer is given by the chatbot

                self.logger.info("MSG_WS_CHATBOT | %s " % (msg))
                self.sendMessage(json.dumps(msg))
            elif msg['msgtype'] == 'edited_nbest':  # Just record this information
                self.logger.info("EDITED_WS_NBEST_RECEIVED | %s " % (msg))
                return
            elif msg['msgtype'] == 'leave':
                self.logger.info("CLOSING | USER - duration: %f",
                                         time.time() - self.start_time)
                on_exit()  # Writes the XML file
            elif msg['msgtype'] == 'chatbot_error':
                self.logger.critical("MSG_WS_RECEIVED | %s " % (msg))
                os._exit(-1)
            else:  # Any other kind of message: just save it
                self.logger.debug("MSG_WS_RECEIVED | %s " % (msg))

        except Exception, e:
            msg['msgtype']= 'chatbot_error'
            msg['error'] = 'Apologize, but there are technical problems and the ' \
                           'chatbot cannot answer you at this moment. Try later'
            self.sendMessage(json.dumps(msg))
            self.logger.error("Unexpected error: %s" % sys.exc_info()[0])
            self.logger.error('Traceback', exc_info=True)
            traceback.print_exc(file=sys.stdout)



    def onClose(self, wasClean, code, reason):
        if not hasattr(self, 'start_time'):
            self.start_time = time.time()

        self.logger.info("CLOSING | %s - duration: %f" % (reason, time.time() - self.start_time))
        self.logger.debug("WS_CLOSED | %s" % reason)


class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = MyClientProtocol

    def __init__(self, *args, **kwargs):
        self.logger = kwargs.pop('logger', None)
        MyClientProtocol.chatbot = kwargs.pop('chatbot', None)
        MyClientProtocol.logger = self.logger
        MyClientProtocol.client_info = kwargs.pop('client_info', None)
        WebSocketClientFactory.__init__(self, *args, **kwargs)

    def clientConnectionFailed(self, connector, reason):
        self.logger.debug("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        self.logger.debug("Client connection lost .. retrying ..")
        self.retry(connector)


def main(args):
    parser = argparse.ArgumentParser(description='Available options for using the chatbot'
                                                 '(i.e. as standalone or websocket-based client')
    parser.add_argument('-a', '--a', action='store_true', help='use as stand-alone application')
    parser.add_argument('-p', '--port', help='port to connect to the server', default=8888)
    parser.add_argument('-t', '--host', help='ip address to connect to the server', default='localhost')
    parser.add_argument('-n', '--name', help='chatbot name', default='ZenMaster')
    parser.add_argument('-l', '--log', help='log filename', default='ZenMaster.log')
    parser.add_argument('-i', '--id', help='chatbot id', default='ISBjFetqtkx7x4V2')
    parser.add_argument('-c', '--config', help='Configuration file', default='zen.cfg')
    args = parser.parse_args(args[1:])

    client = pyClientChatbot(args)
    if args.a:  # Use the app as stand-alone program
        client.start(stand_alone=True)
    else:
        client.start()

if __name__ == '__main__':
    main(sys.argv)

