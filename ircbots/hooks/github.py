from interfaces import Listener, ActionListener

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import cgi, json

from pprint import pformat

class GithubHookHandler(Resource):
    isLeaf = True

    def __init__(self, bot):
        self.bot = bot

    def render_GET(self, request):
        return "MooseBot/0.1 GithubHookHandler\n\r" 

    def render_POST(self, request):
        print "Received Github Hook POST"
        event = request.getHeader('x-github-event')
        if event == "push":
            data = json.loads(request.content.read())

            pusher = str(data['pusher']['name'])
            compare_url = str(data['compare'])
            self.bot.say("%s pushed to the github repository!" % (pusher))
            self.bot.say(compare_url)

        return "OK\n\r"


class GithubHook():
    def __init__(self, *args, **kwargs):
        print "Initializing github hooks"
        resource = GithubHookHandler(kwargs['bot'])
        factory = Site(resource)
        reactor.listenTCP(8880, factory)
