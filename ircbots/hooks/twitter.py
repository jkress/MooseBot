from interfaces import ActionListener

class Twitter():
    self.url        = "http://search.twitter.com/search.json"
    self.listeners  = []

    def __init__(self, *args, **kwargs):
        self.listeners.append( Twitter_ActionListener(*args, **kwargs) )

class Twitter_ActionListener(ActionListener):
    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)
        self.hook('!twitter', self.query_twitter)

    def query_twitter(self, query)

