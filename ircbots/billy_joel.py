from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp
from ircbots.hooks.github import Github

import time, sys

class BillyJoel_Bot(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__ 
        self.modules = [ AutoOp(bot=self), Github(bot=self) ]

    def joined(self, channel):
        self.say("Woof!")

    def privmsg(self, user, channel, msg):
        if self.nickname == channel:
            if msg.startswith("/me "):
                self.me(msg[4:])
            else:
                self.say(msg)

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

