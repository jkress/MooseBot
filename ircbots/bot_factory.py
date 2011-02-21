from twisted.internet import protocol

class BotFactory(protocol.ClientFactory):
    def __init__(self, channel, protocol, server):
        print "BotFactory.__init__"
        self.channel = channel
        self.protocol = protocol
        self.server = server
