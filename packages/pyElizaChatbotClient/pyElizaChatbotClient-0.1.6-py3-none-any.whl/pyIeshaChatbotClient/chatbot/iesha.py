#----------------------------------------------------------------------
#  eliza.py (available at http://www.jezuk.co.uk/cgi-bin/view/software/eliza)
#
#  a cheezy little Eliza knock-off by Joe Strout <joe@strout.net>
#  with some updates by Jeff Epler <jepler@inetnebr.com>
#  hacked into a module and updated by Jez Higgins <jez@jezuk.co.uk>
#  last revised: 28 February 2005
#----------------------------------------------------------------------

import re
import random

class iesha:
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
    [ r'I\'m (.*)',
    [ "ur %1?? that's so cool! kekekekeke ^_^ tell me more!",
      "ur %1? neat!! kekeke >_<"]],

    [ r'(.*) don\'t you (.*)',
    [ "u think I can %2??! really?? kekeke \<_\<",
      "what do u mean %2??!",
      "i could if i wanted, don't you think!! kekeke"]],

    [ r'ye[as] [iI] (.*)',
    [ "u %1? cool!! how?",
      "how come u %1??",
      "u %1? so do i!!"]],

    [ r'do (you|u) (.*)\??',
    [ "do i %2? only on tuesdays! kekeke *_*",
      "i dunno! do u %2??"]],

    [ r'(.*)\?',
    [ "man u ask lots of questions!",
      "booooring! how old r u??",
      "boooooring!! ur not very fun"]],

    [ r'(cos|because) (.*)',
    [ "hee! i don't believe u! >_<",
      "nuh-uh! >_<",
      "ooooh i agree!"]],

    [ r'why can\'t [iI] (.*)',
    [ "i dunno! y u askin me for!",
      "try harder, silly! hee! ^_^",
      "i dunno! but when i can't %1 i jump up and down!"]],

    [ r'I can\'t (.*)',
    [ "u can't what??! >_<",
      "that's ok! i can't %1 either! kekekekeke ^_^",
      "try harder, silly! hee! ^&^"]],

    [ r'(.*) (like|love|watch) anime',
    [ "omg i love anime!! do u like sailor moon??! ^&^",
      "anime yay! anime rocks sooooo much!",
      "oooh anime! i love anime more than anything!",
      "anime is the bestest evar! evangelion is the best!",
      "hee anime is the best! do you have ur fav??"]],

    [ r'I (like|love|watch|play) (.*)',
    [ "yay! %2 rocks!",
      "yay! %2 is neat!",
      "cool! do u like other stuff?? ^_^"]],

    [ r'anime sucks|(.*) (hate|detest) anime',
    [ "ur a liar! i'm not gonna talk to u nemore if u h8 anime *;*",
      "no way! anime is the best ever!",
      "nuh-uh, anime is the best!"]],

    [ r'(are|r) (you|u) (.*)',
    [ "am i %1??! how come u ask that!",
      "maybe!  y shud i tell u?? kekeke >_>"]],

    [ r'what (.*)',
    [ "hee u think im gonna tell u? .v.",
      "booooooooring! ask me somethin else!"]],

    [ r'how (.*)',
    [ "not tellin!! kekekekekeke ^_^",]],

    [ r'(hi|hello|hey) (.*)',
    [ "hi!!! how r u!!",]],

    [ r'quit',
    [ "mom says i have to go eat dinner now :,( bye!!",
      "awww u have to go?? see u next time!!",
      "how to see u again soon! ^_^"]],

    [ r'(.*)',
    [ "ur funny! kekeke",
      "boooooring! talk about something else! tell me wat u like!",
      "do u like anime??",
      "do u watch anime? i like sailor moon! ^_^",
      "i wish i was a kitty!! kekekeke ^_^"]],
  ]

#----------------------------------------------------------------------
#  command_interface
#----------------------------------------------------------------------
def command_interface():
  print("Iesha the TeenBoT\n---------")
  print("Talk to the program by typing in plain English, using normal upper-")
  print('and lower-case letters and punctuation.  Enter "quit" when done.')
  print('='*72)
  print("hi!! i'm iesha! who r u??!")
  s = ""
  chatbot = iesha();
  while s != "quit":
    try: s = raw_input(">")
    except EOFError:
      s = "quit"
      print (s)
    while s[-1] in "!.": s = s[:-1]
    print (chatbot.respond(s))


if __name__ == "__main__":
  command_interface()
