class Hook(object):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs['bot']
        from ircbots.bot_controller import BotController
        self.controller = BotController.create()

class Listener(Hook):
    def __init__(self, *args, **kwargs):
        Hook.__init__(self, *args, **kwargs)

    def listen(self, callback):
        self.bot.registerListener(callback)

class ActionListener(Listener):
    def __init__(self, *args, **kwargs):
        Listener.__init__(self, *args, **kwargs)
        self.actions = {}
        self.listen(( 'privmsg', self.action ))

    def hook(self, action, callback_fn):
        self.actions[action] = callback_fn

    def action(self, user, channel, msg):
        user = user.split('!',1)[0]
        for action in self.actions.keys():
            if msg.startswith(action):
                print "invoking action", action
                self.actions[action](user, channel, msg[len(action):])
