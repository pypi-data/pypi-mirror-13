#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

"""
DESCRIPTION: This package is released in the context of Re-WoChat: Workshop on Collecting
             and Generating Resources for Chatbots and Conversational Agents - Development
             and Evaluation (see further details at http://workshop.colips.org/re-wochat/)
             as part of the shared task (http://workshop.colips.org/re-wochat/shared.html).

USAGE: This program can be run from the command line by using: python pyElizaChatbot.py
       The program can be imported from other python programs using:

       from pyelizachatbotclient import pyElizaChatbot
       client = pyElizaChatbot(name='Eliza', log_file='pyEliza.log')
       client.start()

OUTPUT: A log file called pyEliza.log, unless the user specifies another name during
        the initialization

VERSION: 0.1.4
DATE: Jan/29/2016
AUTHORS: Luis Fernando D'Haro, Rafael E. Banchs
EMAILS: luisdhe@i2r.a-star.edu.sg, rembanchs@i2r.a-star.edu.sg

"""

__version__ = "0.1.4"

# Standard Python Packages
import logging
import sys
import atexit
import random
import string
import time
from builtins import input

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


# Special programs/scripts
from .eliza import eliza
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


class pyElizaChatbot():

    # A dictionary of greetings to get the user's name
    dictNameGreeting = ['Nice to meet you __USR_NAME__ !', '__USR_NAME__ ... What a nice name.',
                        'I am not sure if we have already met __USR_NAME__, but anyway...',
                        'Great __USR_NAME__,']

    # A dictionary of follow up greetings for the chatbot
    dictStartingGreetings = ['What can I do for you?', 'What do you want to talk about?',
                             'How might I help you?', 'How are you doing today?',
                             'How is it going?', 'What''s up?']

    def __init__(self, chatbot_name='Eliza', log_file='pyEliza.log'):
        global _name_logfile
        global _name_chatbot

        self.chatbot_name = chatbot_name
        self.therapist = eliza.eliza()
        self.logger = self.init_logger(log_file)
        _name_logfile = log_file

        self.server_info = {
            'server_url': 'ws://localhost:8888/ws_chat',
            'host': 'localhost',
            'port': 8888,
        }

        self.client_info = {
            "id": 'Ee2oTw5qDMBtiMZ6',  # Identifier to access the server
            "max_users": 1,  # Integer. Indicates how many simultaneous users can handle the chatbot
                             # (WARNING: No implemented yet)
            "image": 'eliza-chatbot.gif',  # Image to show to the users
            "name": self.chatbot_name,  # Official name of the chatbot. Must be different
                              # from others available chatbots
            "description": 'The most famous psychoterapist',  # A short description of the chatbot
        }
        _name_chatbot = chatbot_name


    def init_logger(self, log_file='pyEliza.log',
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

    def start(self):
        global _name_user
        print ('\n***********    WELCOME to pyEliza    ************')
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
                chat_answer = self.therapist.respond(user_input)
                print(self.chatbot_name + ': ' + chat_answer)
                self.logger.info('MSG_CHATBOT | %s' % chat_answer)
                if user_input.lower() == 'bye':
                    self.logger.info("CLOSING | USER - duration: %s",
                                     time.time() - start_time)
                    exit()
            except KeyboardInterrupt:
                self.logger.info("CLOSING | KEYBOARD - duration: %s",
                                 time.time() - start_time)
                exit()
            except Exception as e:
                self.logger.error("ERROR | Unexpected error: %s" % sys.exc_info()[0])
                self.logger.error('Backtrace', exc_info=True)
                exit()

def main():
    client = pyElizaChatbot()
    client.start()


if __name__ == '__main__':
    main()

