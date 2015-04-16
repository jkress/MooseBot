import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('ircbots.cfg')

# getfloat() raises an exception if the value is not a float
# getint() and getboolean() also do this for their respective types
server = config.get('host', 'server')
port  = config.get('host', 'port')
print server + port

# Notice that the next output does not interpolate '%(bar)s' or '%(baz)s'.
# This is because we are using a RawConfigParser().
if config.getboolean('host', 'bool'):
        print config.get('host', 'port')
