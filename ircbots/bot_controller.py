from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

from ircbots.billy_joel import BillyJoel_Bot
#from ircbots.machu_picchu import MachuPicchu
#from ircbots.moose import MooseBot
from ircbots.bot_factory import BotFactory

from ircbots.hooks.auto_op import AutoOp

import ConfigParser
import shelve

class BotController():
    singleton = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read("data/ircbots.cfg")

        self.shelf = shelve.open('data/bot.db', flag='c')

        self.server         = self.getConfig('host', 'server')
        self.port           = int(self.getConfig('host', 'port'))
        self.channel        = self.getConfig('host', 'channel')

        self.billyjoel      = BotFactory(self.channel, BillyJoel_Bot, self)

    @classmethod
    def create(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = cls()
        return cls.singleton

    def getConfig(self, cls, param=None):
        if param:
            return self.config.get(cls, param)
        else:
             return dict(self.config.items(cls))

    def setConfig(self, cls, param, value):
        self.config.set(cls, param, value)
        self.config.write(open("data/ircbots.cfg", 'w'))

    def shelve(self, key, value):
        self.shelf[key] = value
        
    def unshelve(self, key):
        if self.shelf.has_key(key):
            return self.shelf[key]
        else:
            return None

    def start(self):
        if int(self.getConfig('host', 'ssl')):
            print "Connecting to %s:%d over SSL" % (self.server, self.port)
            reactor.connectSSL(self.server, self.port, self.billyjoel, ssl.ClientContextFactory())
        else:
            print "Connecting to %s:%d over TCP" % (self.server, self.port)
            reactor.connectTCP(self.server, self.port, self.billyjoel)

        reactor.run()
        self.finish()

    def finish(self):
        self.shelf.close()
