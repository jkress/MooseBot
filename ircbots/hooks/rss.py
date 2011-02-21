from interfaces import ActionListener
from twisted.internet.task import LoopingCall
import random
import feedparser
print "Importing Linguistics ..."
import en
print "...done"

class Rss():
    
    def __init__(self, *args, **kwargs):
        self.listeners = []
        self.listeners.append( Rss_Listener(*args, **kwargs) )


class Rss_Listener(ActionListener):

    def __init__(self, *args, **kwargs):
        ActionListener.__init__(self, *args, **kwargs)

        self.active = False
        self.feeds = []
        self.entries = {}
        self.keywords = {}
        self.conversation = []

        self.hook('!rss', self.rss )
        self.listen(('privmsg', self.scrape_message))

        self.links = None # self.controller.unshelve('rss-links')
        if not self.links:
            self.links = []

        self.update_feeds_loop = LoopingCall(self._update_feeds)
        self.update_feeds_loop.start(30)
        self.suggest_link_loop = LoopingCall(self._suggest_link)
        self.suggest_link_loop.start(10)

    def scrape_message(self, user, channel, msg):
        self.conversation += [msg]
        print "Conversation buffer:"
        print self.conversation

    def _suggest_link(self):
        if self.active:
            msg = ' '.join(self.conversation)
            print "Trying to suggest a link with ",msg
            channel = self.controller.channel
            keywords = en.content.keywords(msg, nouns=False)
            print msg
            print keywords
            stories = []
            for count, word in keywords:
                if word in self.keywords:
                    stories += self.keywords[word]

            story = random.choice(stories)
            self.bot.say(channel, str("\"%s\"" % (story[0])))
            self.conversation = []

    def _update_feeds(self):
        self.feeds = []
        
        if self.active:
            print "Downloading feeds, trying %d links" % len(self.links)
            for link in self.links:
                try:
                    d = feedparser.parse(link)
                    self.feeds += [ d ]
                    print "Updated feed: %s" % d.feed.title
                except Exception as e:
                    print "Failed: %s" % link
                    print e

            print "Downloaded %d feeds, processing entries" % len(self.feeds)
            for feed in self.feeds:
                try:
                    for entry in feed.entries:
                        print "Processing \"%s\" from feed '%s'" % (entry.title, feed.feed.title)
                        self.entries[entry.link] = entry
                except Exception as e:
                    print "Failed while processing feed"
                    print e

            print "Processing keywords for %d entries" % len(self.entries)
            self.keywords = {}
            for url, entry in self.entries.items():
                print entry.title
                content = ""
                content += entry.title.encode('ascii', 'ignore')
                content += ' '
                content += entry.summary.encode('ascii', 'ignore')
                content = content.translate(None, '\'-\"')
                keywords = en.content.keywords(content.encode('ascii','ignore'), nouns=False)
                old_keywords = keywords
                num_keywords = len(keywords)
                keywords = filter(lambda x: x[0] > 1, keywords)
                rej_keywords = filter(lambda x: x[0] == 1, old_keywords)
                print "Stripping %d keywords, only one mention: %s" % ( num_keywords - len(keywords), ' '.join([x[1] for x in rej_keywords]) )
                print keywords
                for count, keyword in keywords:
                    value = (entry.title, entry.link)
                    if keyword in self.keywords:
                        self.keywords[keyword] += [value]
                    else:
                        self.keywords[keyword] = [value]

            print "Processed keywords"
            from pprint import pprint
            pprint(self.keywords)


    def rss(self, user, channel, msg):
        msg = msg.strip()

        if not msg:
            if self.active:
                self.active = False
                self.bot.say(channel, "I won't mention RSS anymore.")
            else:
                self.active = True
                self.bot.say(channel, "Watching for interesting RSS feeds.")

        elif msg.lower() == 'stats':
            self.bot.say(channel, "I am %sactive." % ("in" if not self.active else ""))
            self.bot.say(channel, "I know about %d links" % len(self.links))
            self.bot.say(channel, "I have %d active feeds" % len(self.feeds))
            self.bot.say(channel, "I have stored %d active entries" % len(self.entries))
            self.bot.say(channel, "I am tracking %d keywords" % len(self.keywords))

        elif msg.lower() == 'keywords':
            idx = 0
            while idx < len(self.keywords):
                self.bot.say(channel, "Keywords: %s" % ' '.join(self.keywords.keys()[idx:idx+50]) )
                idx += 50
        else:
            if msg.startswith("http://"):
                self.links += [msg]
            else:
                self.links += ["http://%s" % msg]
            self.controller.shelve('rss-links',self.links)
            self.bot.describe(channel, "licks %s in the face" % user )
            if not self.active:
                self.active = True
                self.bot.say(channel, "Watching for interesting RSS feeds.")


