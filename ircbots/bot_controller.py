from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

#from ircbots.machu_picchu import MachuPicchu
#from ircbots.billy_joel import BillyJoel
from ircbots.moose import Moose
from ircbots.bot_factory import BotFactory

from ircbots.hooks.auto_op import AutoOp

import ConfigParser
import shelve

class BotController():
    singleton = None

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read("/home/jkress/ircbots/data/ircbots.cfg")

        self.shelf = shelve.open('/home/jkress/ircbots/data/bot.db')

        self.host_config    = self.getConfig('host')
        self.channel        = self.host_config['channel']
        self.port           = int(self.host_config['port'])
        self.server         = self.host_config['server']

        #self.billyjoel      = BotFactory(self.channel, BillyJoel, self)
        #self.machupicchu    = BotFactory(self.channel, MachuPicchu, self)
        self.moosebot       = BotFactory(self.channel, Moose, self)

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

    def setConfig(self, cls, value):
        self.config.set(cls, param, value)

    def shelve(self, key, value):
        self.shelf[key] = value
        
    def unshelve(self, key):
        if self.shelf.has_key(key):
            return self.shelf[key]
        else:
            return None

    def start(self):
        #reactor.connectTCP(self.server, self.port, self.billyjoel)
        #reactor.connectTCP(self.server, self.port, self.machupicchu)
        reactor.connectTCP(self.server, self.port, self.moosebot)
        reactor.run()
        self.finish()

    def finish(self):
        self.shelf.close()
