from interfaces import Listener, ActionListener

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import cgi, json

from pprint import pformat

class Github():
    def __init__(self, *args, **kwargs):
        self.listeners = []
        self.listeners.append( Github_ActionListener(*args, **kwargs) )

class Github_ActionListener(ActionListener):
    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)
        self.listen_port = int(self.controller.getConfig('github', 'listen'))
        self.enabled = int(self.controller.getConfig('github', 'enabled'))

        print "Initializing GitHub Hook Server... listening on %d" % self.listen_port

        resource = GithubHookHandler(self)
        factory = Site(resource)
        reactor.listenTCP(self.listen_port, factory)

        self.hook("!github", self.github_command_handler)

    def github_command_handler(self, user, channel, msg):
        msg_tokens = msg.split()

        if not msg_tokens:
            status = "disabled" if not self.enabled else "enabled, listening on %d" % (self.listen_port)

            self.bot.say("GitHub messages are %s" % (status))
            self.bot.say("!github <on/off>")

        elif msg_tokens[0].lower() in ["off", "quiet", "hide", "disable", "disabled"]:
            self.enabled = False
            self.controller.setConfig('github', 'enabled', '0')
            self.bot.say("GitHub messages are now disabled")

        elif msg_tokens[0].lower() in ["on", "show", "enable", "enabled"]:
            self.enabled = True
            self.controller.setConfig('github', 'enabled', '1')
            self.bot.say("GitHub messages are now enabled")

        else:
            self.bot.say("Not implemented")


class GithubHookHandler(Resource):
    isLeaf = True

    def __init__(self, hook):
        self.hook = hook
        self.bot = hook.bot

    def render_GET(self, request):
        return "MooseBot/0.1 GitHubHookHandler\n\r" 

    def render_POST(self, request):
        print "Received GitHub Hook POST"

        if self.hook.enabled:
            event = request.getHeader('x-github-event')
            data = json.loads(request.content.read())

            if event == "ping":
                repo = str(data['repository']['full_name'])
                url = str(data['repository']['html_url'])

                self.bot.say("Ping from GitHub: [%s] - %s" % (repo, url))

            if event == "push":
                branch = str(data['ref'])[11:]
                repo = str(data['repository']['full_name'])
                pusher = str(data['sender']['login'])
                compare_url = str(data['compare'])
                is_deleted = True if str(data['deleted']) == "True" else False

                commits = []
                for commit in data['commits']:
                    sha = str(commit['id'])[:7]

                    messages = []
                    for msg in str(commit['message']).replace("\r", "").split("\n"):
                        if msg:
                            messages.append(msg)

                    commits.append((sha, messages))

                if is_deleted:
                    self.bot.say("[%s] %s DELETED branch \"%s\"" % (repo, pusher, branch))

                else:
                    self.bot.say("[%s] %s PUSHED to branch \"%s\"" % (repo, pusher, branch))
                    for (sha, messages) in commits:
                        for idx, msg in enumerate(messages):
                            if idx == 0:
                                self.bot.say("(%s): %s" % (sha, msg))
                            else:
                                self.bot.say("           %s" % (msg))

                    self.bot.say(compare_url)

            if event == "pull_request":
                action = str(data['action']).upper()
                merged = data['pull_request']['merged']
                number = int(data['number'])
                user = str(data['sender']['login'])
                title = str(data['pull_request']['title'])
                description = str(data['pull_request']['body']).replace("\r", "")
                branch = str(data['pull_request']['head']['ref'])
                repo = str(data['pull_request']['head']['repo']['full_name'])
                url = str(data['pull_request']['html_url'])

                if action == "SYNCHRONIZE":
                    action = "UPDATED"

                self.bot.say("[%s] %s %s pull request #%d \"%s\" (%s)" % (repo, user, action, number, title, branch))
                if action == "OPENED":
                    for msg in description.split("\n"):
                        if msg:
                            self.bot.say("%s" % (msg))
                if not merged:
                    self.bot.say(url)

        return "OK\n\r"


