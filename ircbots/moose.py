from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp
from ircbots.hooks.connect import Connect

import time, sys

class Moose(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__ 
        self.modules = []

    def joined(self, channel):
        self.modules += [ Connect(bot=self) ]
        self.modules += [ AutoOp(bot=self) ]
        self.say(channel, "Meooowww!")

    def privmsg(self, user, channel, msg):
        if self.nickname == channel:
            self.say(self.factory.channel, msg)

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

