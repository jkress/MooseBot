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
        self.hook("!branch", self.github_branch_handler)

    def github_branch_handler(self, user, channel, msg):
        msg_tokens = msg.split()
        branches = self.controller.getConfig('github', 'branches').strip()
        branches = branches.split(',') if branches else []

        if self.enabled:
            if not msg_tokens:
                if len(branches):
                    plural = "es" if len(branches) > 1 else ""
                    self.bot.say("Monitoring %d branch%s: %s" % (len(branches), plural, ', '.join(branches)))
                self.bot.say("!branch <branch name> to enable/disable branch push notifications")

            elif len(msg_tokens) == 1:
                branch_name = msg_tokens[0]
                if branch_name not in branches:
                    branches += [branch_name]
                    branches.sort()
                    self.controller.setConfig('github', 'branches', ','.join(branches))
                    self.bot.say("Push notifications enabled for branch \"%s\"" % branch_name)

                else:
                    branches = list(set(branches) - set([branch_name]))
                    branches.sort()
                    self.controller.setConfig('github', 'branches', ','.join(branches))
                    self.bot.say("Push notifications removed for branch \"%s\"" % branch_name)


    def github_command_handler(self, user, channel, msg):
        msg_tokens = msg.split()
        branches = self.controller.getConfig('github', 'branches').strip()
        branches = branches.split(',') if branches else []

        if not msg_tokens:
            plural = "es" if len(branches) > 1 or len(branches) == 0 else ""
            status = "disabled" if not self.enabled else "enabled, tracking %d branch%s, listening on %d" % \
                (len(branches), plural, self.listen_port)

            self.bot.say("GitHub messages are %s" % (status))
            self.bot.say("!github <on/off>")
            if self.enabled:
                self.bot.say("!branch <branch name>")

        elif msg_tokens[0].lower() in ["off", "quiet", "hide", "disable", "disabled"]:
            self.enabled = False
            self.bot.say("GitHub messages are now disabled")
            self.controller.setConfig('github', 'enabled', '0')

        elif msg_tokens[0].lower() in ["on", "show", "enable", "enabled"]:
            self.enabled = True
            self.bot.say("GitHub messages are now enabled")
            self.controller.setConfig('github', 'enabled', '1')

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
                ref = str(data['ref'])
                default_branch = str(data['repository']['default_branch'])
                repo = str(data['repository']['full_name'])
                messages = str(data['head_commit']['message']).split('\n')
                added = len(data['head_commit']['added'])
                removed = len(data['head_commit']['removed'])
                modified = len(data['head_commit']['modified'])
                pusher = str(data['sender']['login'])
                compare_url = str(data['compare'])

                branches = self.hook.controller.getConfig('github', 'branches').strip()
                branches = branches.split(',') if branches else []

                if ref == "refs/heads/%s" % default_branch:
                    self.bot.say("[%s] %s PUSHED to branch \"%s\"" % (repo, pusher, default_branch))
                    for m in messages:
                        if m:
                            self.bot.say("| %s" % m)
                    self.bot.say("Files added: %d, removed: %d, modified: %d" % (added, removed, modified))
                    self.bot.say(compare_url)

                elif ref in ["refs/heads/%s" % b for b in branches]:
                    branch_name = ref.split('/')[-1]
                    self.bot.say("[%s] %s PUSHED to branch \"%s\"" % (repo, pusher, branch_name))
                    self.bot.say("Files added: %d, removed: %d, modified: %d" % (added, removed, modified))
                    self.bot.say(compare_url)

            if event == "pull_request":
                action = str(data['action']).upper()
                merged = data['pull_request']['merged']
                number = int(data['number'])
                user = str(data['sender']['login'])
                title = str(data['pull_request']['title'])
                branch = str(data['pull_request']['head']['ref'])
                repo = str(data['pull_request']['head']['repo']['full_name'])
                url = str(data['pull_request']['html_url'])

                if action == "CLOSED" and merged == True:
                    action = "CLOSED and MERGED"

                self.bot.say("[%s] %s %s pull request #%d \"%s\" (%s)" % (repo, user, action, number, title, branch))
                self.bot.say(url)

        return "OK\n\r"


