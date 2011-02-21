from interfaces import ActionListener
import time
import facebook

class Connect():

    def __init__(self, *args, **kwargs):
        self.listeners = []
        self.listeners.append( Connect_ActionListener(*args, **kwargs) )

class Connect_ActionListener(ActionListener):

    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)
        self.hook('!facebook', self.login)
        self.hook('!check', self.check_notifications)
        self.hook('!status', self.set_status)
        self.hook('!feed', self.watch_newsfeed)
        self.fb      = {} # Store an instance of Facebook for each user who asks to connect
        self.session = {}
        self.newsfeed= {} # Store the newsfeed functions, None means newsfeed monitoring is Off
        stored_session = self.controller.unshelve('facebook-sessions')
        if stored_session: 
            self.session = stored_session
            for user, session in stored_session.items():
                self.fb[user] = facebook.Facebook('5496c69964cb75fb3014c5112d22c31a',
                                                  '63b189430aefa9404e13e8ee4a874467')

                self.fb[user].secret = session['secret']
                self.fb[user].session_key = session['session_key']
                self.newsfeed[user] = None

    def login(self, user, channel, msg):
        if self._do_connect(user, channel, msg):
            session = self.session[user]
            name = self.fb[user].users.getInfo(session['uid'], ['name'])[0]
            self.bot.say(channel, "%s: You are logged into Facebook as %s" % (user, str(name['name'])))

    # This should be called before every action.
    # Returns False : The user needs to visit the URL to log in.
    # Returns True : The user is or has just successfully logged in.
    def _do_connect(self, user, channel, msg):

        # See if we already have a token for this user
        if user in self.fb.keys():

            # If we do not yet have a session, get the session.
            # This will fail unless the user has visited the login url.
            if not self.session[user]:
                self.session[user] = session = self.fb[user].auth.getSession()
                self.session[user]['secret'] = self.fb[user].secret
                self.controller.shelve('facebook-sessions',self.session)
                name = self.fb[user].users.getInfo(session['uid'], ['name'])[0]
                self.bot.say(channel, "%s: Welcome to Facebook, %s" % (user,str(name['name'])))

            # Return True, proceed to query against self.fb[user]
            return True

        # New user needs to be connected
        else:

            # Create a FB object for this user, create a token and ask them to connect
            self.fb[user] = facebook.Facebook('5496c69964cb75fb3014c5112d22c31a','63b189430aefa9404e13e8ee4a874467')
            self.fb[user].auth.createToken()
            self.session[user] = None
            self.newsfeed[user] = None
            self.bot.say(channel, "%s: Log into Facebook, then try again" % (user) )
            self.bot.say(channel, "%s: %s" % (user, self.fb[user].get_login_url()) )

            # Advise that we cannot proceed; the user needs to log in / connect to our mojo
            return False

    def get_extended_permission(self, user, channel, msg, permission):
        self.bot.say(channel, "%s: I need permission for this :/" % user)
        self.bot.say(channel, "%s: %s" % (user, self.fb[user].get_ext_perm_url(permission))) 
        
    def check_notifications(self, user, channel, msg):
        # Check and/or handle login first
        if self._do_connect(user, channel, msg):
            notifications = self.fb[user].notifications.get()
            responses = []
            if notifications['event_invites']:
                num = len(notifications['event_invites'])
                responses += ["%d event %s" % ( num, "invite" if num == 1 else "invites")]

            if notifications['friend_requests']:
                num = len(notifications['friend_requests'])
                responses += ["%d friend %s" % ( num, "request" if num == 1 else "requests" )]

            if notifications['group_invites']:
                num = len(notifications['group_invites'])
                responses += ["%d group %s" % (num, "invite" if num == 1 else "invites" )]

            if int(notifications['messages']['unread']) > 0:
                num = int(notifications['messages']['unread'])
                responses += ["%s unread %s" % (num, "message" if num == 1 else "messages" )]

            if int(notifications['pokes']['unread']) > 0:
                num = int(notifications['pokes']['unread'])
                responses += ["%s %s" % (num, "poke" if num == 1 else "pokes" )]

            if int(notifications['shares']['unread']) > 0:
                num = int(notifications['shares']['unread'])
                responses += ["%s %s" % (num, "share" if num == 1 else "shares" )]

            if responses:
                self.bot.say(channel, "%s: You have %s" % (user, ', '.join(responses)))
            else:
                self.bot.say(channel, "%s: No notifications" % user) 

    def set_status(self, user, channel, msg):
        if self._do_connect(user,channel,msg):
            try:
                msg = msg.strip()
                session = self.session[user]
                name = str(self.fb[user].users.getInfo(session['uid'], ['name'])[0]['name'])

                if msg:
                    response = self.fb[user].users.setStatus(msg,False, status_includes_verb=True)

                    if response:
                        self.bot.say(channel, "%s %s" % (name, msg))
                else:
                    current_status = self.fb[user].users.getInfo(session['uid'],['status'])[0]['status']['message']
                    if current_status:
                        self.bot.say(channel, "%s %s" % ( name, str(current_status)))
                    else:
                        self.bot.say(channel, "%s has a blank status. :(" % (name))
            except facebook.FacebookError as e:
                self.get_extended_permission(user, channel, msg, 'status_update')

    def watch_newsfeed(self, user, channel, msg):
        if self._do_connect(user, channel, msg):
            if not self.newsfeed[user]:
                from twisted.internet.task import LoopingCall
                checkFn = LoopingCall(self._do_watch_newsfeed, user, channel, msg)
                time = int(msg) if msg else 30
                checkFn.start(time)
                self.newsfeed[user] = checkFn
                self.bot.say(channel, "%s: Newsfeed monitoring On (%d seconds)" % (user, time))
            else:
                if self.newsfeed[user]:
                    self.newsfeed[user].stop()
                self.newsfeed[user] = None
                self.bot.say(channel, "%s: Newsfeed monitoring Off" % user)

    def _do_watch_newsfeed(self, user, channel, msg):
        print "_do_watch_newsfeed for %s in %s fired at %d" % (user, channel, int(time.time()))
        try:
            check_time = int(time.time() - 30)
            uid = self.session[user]['uid']

            status_stream_key = self.fb[user].fql.query("SELECT filter_key, name FROM stream_filter WHERE uid=%s AND name='Status Updates'" % uid)[0]['filter_key']

            results = self.fb[user].fql.query("SELECT actor_id, message FROM stream WHERE filter_key == '%s' and updated_time > %d" % (status_stream_key, check_time))
            for item in results:
                actor   = self.fb[user].fql.query("SELECT name FROM user WHERE uid == '%s' LIMIT 1" % item['actor_id'])[0]['name']
                message = item['message']
                self.bot.say(channel, str("%s %s" % (actor, message)))
        except facebook.FacebookError:
            self.bot.say(channel, "%s: Your permissions probably restrict this" % user)
            self.get_extended_permission(user, channel, msg, 'read_stream')

