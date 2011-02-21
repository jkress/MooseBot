from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from bot import Bot
from ircbots.hooks.auto_op import AutoOp
import time, sys

class MachuPicchu(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.nickname = self.__class__.__name__
        self.modules = []
        print self.nickname

    def joined(self, channel):
        self.modules += [ AutoOp(bot=self) ]
        self.say(channel,"Ruff and all that stuff!!!!")

    def privmsg(self, user, channel, msg):
        pass

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        print "action from", user
    
    def userJoined(self, user, channel):
        self.say(channel,"Woof!! Hello " + user + " welcome to Diamondtown.  Where dogs are androids and androids are dogs.")
        Bot.userJoined(self, user, channel)
