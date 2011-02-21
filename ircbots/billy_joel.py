from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp
from ircbots.hooks.connect import Connect
from ircbots.hooks.rss     import Rss

import time, sys

class BillyJoel(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__ 
        self.modules = []

    def joined(self, channel):
        self.modules += [ Connect(bot=self), Rss(bot=self) ]
        self.describe(channel, "Looks around for cats")

    def privmsg(self, user, channel, msg):
        pass

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

