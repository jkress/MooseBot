from interfaces import Listener, ActionListener

class AutoOp():
    def __init__(self, *args, **kwargs):
        self.listeners = []
        self.listeners.append( AutoOp_Listener(*args, **kwargs) )
        self.listeners.append( AutoOp_ActionListener(*args, **kwargs) )

class AutoOp_Listener(Listener):
    def __init__(self, *args, **kwargs):
        Listener.__init__(self, *args, **kwargs)
        self.listen(('userJoined', self.verify_op_join))

    def verify_op_join(self, *args, **kwargs):
        username = args[0]
        channel  = args[1]
        auto_op_user_list = self.controller.getConfig('AutoOp','users')
        if username in auto_op_user_list:
            self.bot.say(channel,"%s: you get op! arf!" % username)
            self._do_auto_op(username, channel)

    def _do_auto_op(self, name, channel):
        self.bot.mode(channel, True, 'o', user=name)

class AutoOp_ActionListener(ActionListener):
    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)
        self.hook('!op', self.auto_op_handler)
        
    def auto_op_handler(self, user, channel, msg):
        msg_tokens = msg.lower().split()

        user_list = None   # Get the user list from the bot
        
        if not msg_tokens:
            # Op the requesting user
            self.bot.say(channel, "%s: Op'ing you just this once" % user)

        elif msg_tokens[0] in ['auto','add','set','save']:
            # Op them, and add them to the persistent auto_op_user_list
            self.bot.say(channel, "Adding to persistent auto_op")
            
