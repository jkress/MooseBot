from interfaces import Listener, ActionListener
import time, os, datetime

class Logger():
    def __init__(self, *args, **kwargs):
        self.listeners = []
        self.listeners.append( Logger_Listener(*args, **kwargs) )
        self.listeners.append( Logger_ActionListener(*args, **kwargs) )

class Logger_Listener(Listener):
    def __init__(self, *args, **kwargs):
        Listener.__init__(self, *args, **kwargs)

        self.listen(('say', self.bot_message))
        self.listen(('me', self.bot_action))
        self.listen(('privmsg', self.message))
        self.listen(('action', self.action))
        self.listen(('modeChanged', self.mode_changed))
        self.listen(('userJoined', self.user_joined))
        self.listen(('userLeft', self.user_left))
        self.listen(('userQuit', self.user_quit))
        self.listen(('userRenamed', self.nick_changed))
        self.listen(('topicUpdated', self.topic_changed))

    def prepare_log(self):
        log_path = self.controller.getConfig('logger', 'path')
        midnight = int(time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time.min).timetuple()))
        log_name = "%s_%s.log" % (self.controller.channel.strip("#"), midnight)

        self.logfile = open(os.path.join(log_path, log_name), 'a')

    def do_log(self, user, message):
        if int(self.controller.getConfig('logger', 'enabled')):
            self.prepare_log()

            timestamp = time.strftime("[%H:%M]", time.localtime(time.time()))
            user = user if user else "* "

            self.logfile.write('%s %s: %s\n' % (timestamp, user.rjust(18), message))
            self.logfile.flush()
            self.logfile.close()

    def bot_message(self, message):
        self.do_log(self.bot.nickname, message)

    def bot_action(self, message):
        self.do_log(None, "%s %s" % (self.bot.nickname, message))

    def message(self, username, channel, message):
        user = username.split('!', 1)[0]
        if channel == self.controller.channel:
            self.do_log(user, message)

    def action(self, username, channel, message):
        user = username.split('!', 1)[0]
        if channel == self.controller.channel:
            self.do_log(None, "%s %s" % (user, message))

    def mode_changed(self, username, channel, setBool, mode, args):
        user = username.split('!', 1)[0]
        target = args[0]
        plus_minus = "+" if setBool else "-"

        if channel == self.controller.channel:
            if target:
                self.do_log(None, "%s set mode %s%s on user %s" % (user, plus_minus, mode, target))
            else:
                self.do_log(None, "%s set mode %s%s on %s" % (user, plus_minus, mode, channel))

    def user_joined(self, user, channel):
        if channel == self.controller.channel:
            self.do_log(None, "%s joined the channel %s" % (user, channel))

    def user_left(self, user, channel):
        if channel == self.controller.channel:
            self.do_log(None, "%s left the channel %s" % (user, channel))

    def user_quit(self, user, quitMessage):
        self.do_log(None, "%s has quit (%s)" % (user, quitMessage))

    def nick_changed(self, oldName, newName):
        self.do_log(None, "%s is now known as %s" % (oldName, newName))

    def topic_changed(self, user, channel, newTopic):
        if channel == self.controller.channel:
            self.do_log(None, "%s set the topic: %s" % (user, newTopic))

class Logger_ActionListener(ActionListener):
    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)

        self.hook('!log', self.log_command_handler)
        self.hook('!logger', self.log_command_handler)
        
    def log_command_handler(self, user, channel, msg):
        msg_tokens = msg.split()

        enabled = int(self.controller.getConfig('logger', 'enabled'))
        log_url = "%s%s" % (self.controller.getConfig('logger', 'url'), self.controller.channel.strip('#'))

        if not msg_tokens:
            status = "enabled" if enabled else "disabled"
            self.bot.say("The channel logger is %s" % (status))
            self.bot.say("View channel logs: %s" % (log_url))

        elif msg_tokens[0].lower() in ["on", "enable", "enabled", "start"]:
            self.controller.setConfig('logger', 'enabled', '1')
            self.bot.say("Logging is now enabled")

        elif msg_tokens[0].lower() in ["off", "disable", "disabled", "stop"]:
            self.controller.setConfig('logger', 'enabled', '0')
            self.bot.say("Logging is now disabled")

        else:
            self.bot.say("Not implemented")
