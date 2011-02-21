from distutils.core import setup

setup(
        name = 'ircbots',
        version = '0.0.1',
        url = 'http://irc.diamondtown.org',
        author = "Billy Joel",
        author_email = "amckinley@facebook.com",
        packages = [ 'ircbots', 'ircbots.hooks' ],
        #scripts = [ 'scripts/newhotness', 'scripts/fpl' ]
)
