from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import time, sys

class Bot(irc.IRCClient, object):
    def __init__(self):
        self.listeners = []

    def registerListener(self, listener):
        self.listeners.append(listener)

    def __getattribute__(self, name):
        # We need self.listeners. Try as hard as you can to get it. 
        listeners = []
        try:
            listeners = object.__getattribute__(self,'listeners')
        except AttributeError:
            return object.__getattribute__(self,name)

        listeners = filter( (lambda x: x[0] == name), listeners )
        def capture(*args, **kwargs):
            for _ , fn in listeners:
                fn(*args, **kwargs)
            object.__getattribute__(self,name)(*args, **kwargs)

        # If we are calling a method we have a listener for, return capture function
        if listeners:
            return capture
        else:
            return object.__getattribute__(self,name)

    def connectionMade(self):
        print "ConnectionMade"
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        print "ConnectionLost"
        irc.IRCClient.connectionLost(self)

    def signedOn(self):
        print "signedOn"
        self.join(self.factory.channel)

