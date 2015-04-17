from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp
from ircbots.hooks.github import Github
from ircbots.hooks.logger import Logger

import time, sys
from random import randint

class BillyJoel_Bot(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__ 
        self.modules = [ Logger(bot=self), AutoOp(bot=self), Github(bot=self) ]

    def joined(self, channel):
        self.say("Woof!")

    def privmsg(self, user, channel, msg):
        if self.nickname == channel:
            if msg.startswith("/me "):
                self.me(msg[4:])
            else:
                self.say(msg)
        
        else:
            user = user.split('!', 1)[0]
            if self.nickname in msg:
                if randint(0,1):
                    self.say("%s: Woof!" % user)
                else:
                    self.me("wags his tail")

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

