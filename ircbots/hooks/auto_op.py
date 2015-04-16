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
        auto_op_user_list = self.controller.getConfig('AutoOp','users').split(',')
        if username in auto_op_user_list:
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
        auto_op_user_list = self.controller.getConfig('AutoOp', 'users').split(',')
        
        if not msg_tokens:
            self.bot.say("Auto-op list: %s" % (','.join(auto_op_user_list)))
            self.bot.say("!op <user> to add/remove")

        elif msg_tokens[0] in ['auto','add','set','save']:
            # Op them, and add them to the persistent auto_op_user_list
            self.bot.say("Not implemented")

        else:
            # Assume the argument is a user, try to op that user
            new_op_user = msg_tokens[0]
            if user in auto_op_user_list:
                if new_op_user not in auto_op_user_list:
                    self.bot.say("Adding %s to the Auto-op list" % new_op_user)
                    auto_op_user_list += [new_op_user]
                    self.controller.setConfig('AutoOp', 'users', ','.join(auto_op_user_list))
                    self.bot.mode(channel, True, 'o', user=new_op_user)

                else:
                    self.bot.say("Removing %s from the Auto-op list" % new_op_user)
                    auto_op_user_list = set(auto_op_user_list) - set([new_op_user])
                    self.controller.setConfig('AutoOp', 'users', ','.join(auto_op_user_list))
                    self.bot.mode(channel, False, 'o', user=new_op_user)

            else:
                self.bot.say("%s: You're not on the list" % user)
            
