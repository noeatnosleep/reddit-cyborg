import praw
import json
import yaml
import os
import re
from collections import deque
import time

#Globals

r=praw.Reddit('reddit cyborg by /u/captainmeta4')

SUBREDDIT = r.get_subreddit('redditcyborg')
ME = r.get_redditor('captainmeta4')

DISCLAIMER = "\n\n*^(I am a cyborg, and this action was performed automatically. Please message the moderators with any concerns.)"

class Rule():

    #Rule object which stores rule data

    _valid_args=[
        'subreddit',
        'author_name',
        'action',
        'body'
        ]

    def __init__(self, data={}):

        self.data=data

        self.subreddit = []
        self.type = "both"
        self.author_name = []
        self.body = []
        self.body_regex = []

        self.action = []
        self.reason = ""
        self.comment = ""
        self.ban_message = ""

        if 'type' in data:
            self.type = data['type']

        if 'subreddit' in data:
            self.subreddit = data['subreddit']

        if 'author_name' in data:
            self.author_name = data['author_name']
            
        if 'body' in data:
            self.body = data['body']

        if 'body_regex' in data:
            self.body_regex = data['body_regex']

        if 'action' in data:
            self.action = data['action']

        if 'reason' in data:
            self.reason = data['reason']

        if 'comment' in data:
            self.comment = data['comment']

        if 'ban_message' in data:
            self.ban_message = data['ban_message']
                
    def __str__(self):
        return yaml.dump(self.data)

    def evaluate_thing(self, thing):

        #begin checking
        if self.type=="both":
            pass
        elif isinstance(thing, praw.objects.Comment):
            if "submission" in self.type:
                return
        elif isinstance(thing, praw.objects.Submission):
            if self.type == "comment":
                return
            elif self.type == "link submission" and thing.url == thing.permalink:
                return
            elif self.type == "text submission" and thing.url != thing.permalink:
                return

        if self.subreddit:
            if not any(x.lower()==thing.subreddit.display_name.lower() for x in self.subreddit):
                print('subreddit mismatch')
                return

        if self.author_name:
            if thing.author is not None:
                if not any(x.lower()==thing.author.name.lower() for x in self.author_name):
                    print('author mismatch')
                    return

        if self.body:
            try:
                if isinstance(thing, praw.objects.Comment):
                    if not any(x.lower()==y.lower() for x in thing.body.split() for y in self.body):
                        print('body mismatch')
                        return
                elif isinstance(thing, praw.objects.Submission):
                    if not any(x.lower()==y.lower() for x in thing.selftext.split() for y in self.body):
                        print('body mismatch')
                        return
            except AttributeError:
                print('body error')
                return

        if self.body_regex:
            try:
                if isinstance(thing, praw.objects.Comment):
                    if not any(re.search(x.lower(), thing.body.lower()) for x in self.body_regex):
                        print('body regex mismatch')
                        return
                elif isinstance(thing, praw.objects.Submission):
                    if not any(re.search(x.lower(), thing.selftext.lower()) for x in self.body_regex):
                        print('body regex mismatch')
                        return
            except AttributeError:
                print('body regex error')
                return


        #at this point all criteria are satisfied. Act.
        print("rule triggered at "+thing.permalink)

        #see if we need to fetch the parent thing
        #if we do but it's not a comment then return
        if any("parent" in x for x in self.action):
            if isinstance(thing, praw.objects.Comment):
                parent=r.get_info(thing_id=thing.parent_id)
            else:
                return
            

        #do all actions

        if "remove" in self.action:
            thing.remove()

        if "remove_parent" in self.action:
            parent.remove()

        if "spam" in self.action:
            thing.remove(spam=True)

        if "spam_parent" in self.action:
            parent.remove(spam=True)

        if "ban" in self.action:
            thing.subreddit.add_ban(thing.author, note=self.reason, ban_message=self.ban_message)

        if "ban_parent" in self.action:
            thing.subreddit.add_ban(parent.author, note=self.reason, ban_message=self.ban_message)

        if "report" in self.action:
            thing.report(reason=self.reason)

        if "report_parent" in self.action:
            parent.report(reason=self.reason)

        if "approve" in self.action:
            thing.approve()

        if "approve_parent" in self.action:
            parent.approve()

        if "rts" in self.action:
            r.submit("spam", "Overview for /u/"+thing.author.name, url="http://reddit.com/user/"+thing.author.name)

        if "rts_parent" in self.action:
            r.submit("spam", "Overview for /u/"+parent.author.name, url="http://reddit.com/user/"+parent.author.name)

        if self.comment:
            comment.reply(self.comment).distinguish()
        

class Bot():

    def __init__(self):

        self.rules=[]

        self.already_done = deque([],maxlen=400)

    def run(self):

        self.login()
        self.load_rules()
        self.mainloop()

    def login(self):

        r.login(ME, os.environ.get('password'), disable_warning=True)

    def load_rules(self):

        #get wiki page

        print('loading rules...')
        wiki_page = r.get_wiki_page(SUBREDDIT, "users/"+ME.name).content_md

        for entry in yaml.safe_load_all(wiki_page):
            self.rules.append(Rule(data=entry))
        print('...done')

    def reload_rules(self):
        print('Rules reload ordered')
        self.rules=[]
        self.load_rules()


    def full_stream(self):
        #unending generator which returns content from /new, /comments, and /edited of /r/mod

        subreddit = r.get_subreddit('mod')

        start_time = int(time.time())
        

        while True:
            single_round_stream = []

            #fetch /new
            print('fetching /new')
            for submission in subreddit.get_new(limit=100):

                #avoid old work (important for bot startup)
                if submission.created_utc < start_time:
                    continue

                #avoid duplicate work
                if submission.fullname in self.already_done:
                    continue
                
                self.already_done.append(submission.fullname)
                single_round_stream.append(submission)

            #fetch /comments
            print('fetching /comments')
            for comment in subreddit.get_comments(limit=100):

                #avoid old work
                if comment.created_utc < start_time:
                    continue

                #avoid duplicate work
                if comment.fullname in self.already_done:
                    continue
                self.already_done.append(comment.fullname)
                single_round_stream.append(comment)

            #fetch /edited
            print('fetching /about/edited')
            for thing in subreddit.get_edited(limit=100):
                #ignore removed things
                if thing.banned_by:
                    continue

                if thing.edited < start_time:
                    continue
                
                #uses duples so that new edits are detected but old edits are passed by
                #.edited is the edit timestamp (False on unedited things)
                if (thing.fullname, thing.edited) not in self.already_done:
                    continue
                
                self.already_done.append((thing.fullname, thing.edited))
                single_round_stream.append(thing)

            for thing in single_round_stream:

                yield thing

    def mainloop(self):

        for thing in self.full_stream():
            print('checking thing '+thing.fullname+' by /u/'+thing.author.name+' in /r/'+thing.subreddit.display_name)

            #hard code rule reload
            if isinstance(thing, praw.objects.Comment):
                if thing.author==ME and thing.body=="!reload":
                    thing.delete()
                    self.reload_rules()
                    continue
            
            for rule in self.rules:
                rule.evaluate_thing(thing)


if __name__=="__main__":
    b=Bot()
    b.run()
