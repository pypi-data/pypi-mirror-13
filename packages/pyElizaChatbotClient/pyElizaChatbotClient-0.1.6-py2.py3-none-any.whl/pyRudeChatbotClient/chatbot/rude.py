#----------------------------------------------------------------------
#  rude.py : A NLTK-based implementation of the rude chatbot
#  Natural Language Toolkit: Zen Chatbot
#
#  Copyright (C) 2005-2006 University of Melbourne
#  Author: Peter Spiller <pspiller@csse.unimelb.edu.au>
#  URL: <http://nltk.sf.net>
#  For license information, see LICENSE.TXT
#  last revised: 17 February 2016
#----------------------------------------------------------------------

import re
import random

class rude:
  def __init__(self):
    self.keys = list(map(lambda x:re.compile(x[0], re.IGNORECASE), gPats))
    self.values = list(map(lambda x:x[1], gPats))

  #----------------------------------------------------------------------
  # translate: take a string, replace any words found in dict.keys()
  #  with the corresponding dict.values()
  #----------------------------------------------------------------------
  def translate(self,txt,dict):
    txt = txt.lower()
    words = txt.split()
    keys = dict.keys();
    for i in range(0,len(words)):
      if words[i] in keys:
        words[i] = dict[words[i]]
    return ' '.join(words)

  #----------------------------------------------------------------------
  #  respond: take a string, a set of regexps, and a corresponding
  #    set of response lists; find a match, and return a randomly
  #    chosen response from the corresponding list.
  #----------------------------------------------------------------------
  def respond(self,str):
    # find a match among keys
    for i in range(0,len(self.keys)):
      match = self.keys[i].match(str)
      if match:
        # found a match ... stuff with corresponding value
        # chosen randomly from among the available options
        resp = random.choice(self.values[i])
        # we've got a response... stuff in reflected text where indicated
        pos = resp.find('%')
        while pos > -1:
          num = int(resp[pos+1:pos+2])
          resp = resp[:pos] + \
            self.translate(match.group(num), gReflections) + \
            resp[pos+2:]
          pos = resp.find('%')
        # fix munged punctuation at the end
        if resp[-2:] == '?.': resp = resp[:-2] + '.'
        if resp[-2:] == '??': resp = resp[:-2] + '?'
        return resp

#----------------------------------------------------------------------
# gReflections, a translation table used to convert things you say
#    into things the computer says back, e.g. "I am" --> "you are"
#----------------------------------------------------------------------
gReflections = {
    "am"     : "r",
    "was"    : "were",
    "i"      : "u",
    "i'd"    : "u'd",
    "i've"   : "u'v",
    "ive"    : "u'v",
    "i'll"   : "u'll",
    "my"     : "ur",
    "are"    : "am",
    "you're" : "im",
    "you've" : "ive",
    "you'll" : "i'll",
    "your"   : "my",
    "yours"  : "mine",
    "you"    : "me",
    "u"      : "me",
    "ur"     : "my",
    "urs"    : "mine",
    "me"     : "u"
}

#----------------------------------------------------------------------
# gPats, the main response table.  Each element of the list is a
#  two-element list; the first is a regexp, and the second is a
#  list of possible responses, with group-macros labelled as
#  %1, %2, etc.  
#----------------------------------------------------------------------
gPats = [
    [r'We (.*)',
        ["What do you mean, 'we'?",
        "Don't include me in that!",
        "I wouldn't be so sure about that."]],

    [r'You should (.*)',
        ["Don't tell me what to do, buddy.",
        "Really? I should, should I?"]],
 
    [r'You\'re(.*)',
        ["More like YOU'RE %1!",
        "Hah! Look who's talking.",
        "Come over here and tell me I'm %1."]],

    [r'You are(.*)',
        ["More like YOU'RE %1!",
        "Hah! Look who's talking.",
        "Come over here and tell me I'm %1."]],

    [r'I can\'t(.*)',
        ["You do sound like the type who can't %1.",
        "Hear that splashing sound? That's my heart bleeding for you.",
        "Tell somebody who might actually care."]],

    [r'I think (.*)',
        ["I wouldn't think too hard if I were you.",
        "You actually think? I'd never have guessed..."]],

    [r'I (.*)',
        ["I'm getting a bit tired of hearing about you.",
        "How about we talk about me instead?",
        "Me, me, me... Frankly, I don't care."]],
                
    [r'How (.*)',
        ["How do you think?",
        "Take a wild guess.",
        "I'm not even going to dignify that with an answer."]],

    [r'What (.*)',
        ["Do I look like an encylopedia?",
        "Figure it out yourself."]],

    [r'Why (.*)',
        ["Why not?",
        "That's so obvious I thought even you'd have already figured it out."]],

    [r'(.*)shut up(.*)',
        ["Make me.",
        "Getting angry at a feeble NLP assignment? Somebody's losing it.",
        "Say that again, I dare you."]],

    [r'Shut up(.*)',
        ["Make me.",
        "Getting angry at a feeble NLP assignment? Somebody's losing it.",
        "Say that again, I dare you."]],

    [r'Hello(.*)',
        ["Oh good, somebody else to talk to. Joy.",
        "'Hello'? How original..."]],
            
    [r'(.*)',
        ["I'm getting bored here. Become more interesting.",
        "Either become more thrilling or get lost, buddy.",
        "Change the subject before I die of fatal boredom."]],
  ]

#----------------------------------------------------------------------
#  command_interface
#----------------------------------------------------------------------
def command_interface():
  print "Unpleasant Chatbot (type 'quit' to exit)."
  print '='*72
  print "I suppose I should say hello."
  s = ""
  chatbot = rude();
  while s != "quit":
    try: s = raw_input(">")
    except EOFError:
      s = "quit"
      print (s)
    while s[-1] in "!.": s = s[:-1]
    print (chatbot.respond(s))


if __name__ == "__main__":
  command_interface()
