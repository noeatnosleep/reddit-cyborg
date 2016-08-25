import praw
import json
import yaml
import os
import re

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

        self.subreddit = []
        self.author_name = [],
        self.body = [],
        self.body_regex = []

        self.action = [],
        self.reason = "",
        self.comment = ""
        self.ban_message = ""

        if 'subreddit' in data:
            self.subreddit = data['subreddit']

        if 'author_name' in data:
            self.subreddit = data['author_name']
        if 'body' in data:
            self.subreddit = data['body']

        if 'body_regex' in data:
            self.subreddit = data['body_regex']

        if 'action' in data:
            self.subreddit = data['action']

        if 'reason' in data:
            self.subreddit = data['reason']

        if 'comment' in data:
            self.subreddit = data['comment']

        if 'ban_message' in data:
            self.subreddit = data['ban_message']

    def evaluate_comment(self, comment):

        #begin checking

        if self.subreddit:
            if not any(x.lower()==comment.subreddit.display_name.lower() for x in self.subreddit):
                print('mismatched at subreddit')
                return

        if self.author_name:
            if comment.author is not None:
                if not any(x.lower()==comment.author.name.lower() for x in self.author_name):
                    print('mismatched at authorname')
                    return

        if self.body:
            if not any(x.lower()==y.lower() for x in comment.body.split() for y in self.body):
                print('mismatched at body')
                return

        if self.body_regex:
            if not any(re.search(x.lower(), comment.body.lower()) for x in self.body_regex):
                print('mismatched at body_regex')
                return


        #at this point all criteria are satisfied. Act.
        print("rule triggered at "+comment.permalink)

        #see if we need to fetch the parent thing
        if any("parent" in x for x in self.action):
            parent=r.get_info(thing_id=comment.parent_id)

        #do all actions

        if "remove" in self.action:
            comment.remove()

        if "remove_parent" in self.action:
            parent.remove()

        if "spam" in self.action:
            comment.remove(spam=True)

        if "spam_parent" in self.action:
            parent.remove(spam=True)

        if "ban" in self.action:
            comment.subreddit.add_ban(comment.author, note=self.reason, ban_message=self.ban_message)

        if "ban_parent" in self.action:
            comment.subreddit.add_ban(parent.author, note=self.reason, ban_message=self.ban_message)

        if "report" in self.action:
            comment.report(reason=self.reason)

        if "report_parent" in self.action:
            parent.report(reason=self.reason)

        if "approve" in self.action:
            comment.approve()

        if "approve_parent" in self.action:
            parent.approve()

        if "rts" in self.action:
            r.submit("spam", "Overview for /u/"+comment.author.name, url="http://reddit.com/user/"+comment.author.name)

        if "rts_parent" in self.action:
            r.submit("spam", "Overview for /u/"+parent.author.name, url="http://reddit.com/user/"+parent.author.name)

        if self.outputs['comment']:
            comment.reply(self.outputs['comment']).distinguish()
        

class Bot():

    def __init__(self):

        self.rules=[]

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


    def mainloop(self):

        for comment in praw.helpers.comment_stream(r, "mod", limit=100, verbosity=0):
            print('checking comment by /u/'+comment.author.name)

            #hard code rule reload
            if comment.author==ME and comment.body=="!reload"
                comment.delete()
                self.reload_rules()
            
            for rule in self.rules:
                print('checking rule #'+str(self.rules.index(rule)))
                rule.evaluate_comment(comment)
        

        

    def process_signups(self):

        #get new, unflaired submissions

        for submission in SUBREDDIT.get_new(limit=100):

            #end on submissions that have already been evaluated
            if submission.flair_css_class == "signed up":
                break

            #get username:
            if submission.author == None:
                continue
            username = submission.author.name

            #check to make sure it's not a duplicate
            try:
                wiki = r.get_wiki_page(SUBREDDIT, 'users/'+username).content_md
                continue
            except praw.errors.NotFound:
                pass

            text = "###### If you edit this page, you must [click this link, then click 'send'](http://www.reddit.com/message/compose/?to=reddit_cyborg&subject=%update&message=update) to have RedditCyborg re-load the rules from here"

            r.edit_wiki_page(SUBREDDIT, 'users/'+username, text)


if __name__=="__main__":
    b=Bot()
    b.run()
