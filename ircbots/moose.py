from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp

import time, sys

class MooseBot(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__ 
        self.modules = []

    def joined(self, channel):
        self.modules += [ AutoOp(bot=self) ]
        self.say("Meooowww!")

    def privmsg(self, user, channel, msg):
        if self.nickname == channel:
            self.say(msg)

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

