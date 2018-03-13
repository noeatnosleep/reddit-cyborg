import praw
import time

'''
Script to count mod actions since the beginning of this month
'''

r=praw.Reddit('me')

actions=[]
me = r.user.me()

#get current month
month = time.gmtime().tm_mon

#iterate through moderated subreddits
for subreddit in r.user.moderator_subreddits(limit=None):

    print('evaluating /r/{}'.format(subreddit.display_name))

    action_count=0

    for action in subreddit.mod.log(limit=None, mod=me.name):

        #if item is older than midnight on the morning of the first of the month, end iteration
        if time.gmtime(action.created_utc).tm_mon != month:
            break

        action_count +=1

    #if at least 1 action was performed this month, add it to list
    if action_count > 0:
        actions.append((subreddit.display_name,action_count))

#sort list in descending order
actions = sorted(actions,key = lambda tup: tup[1], reverse=True)

#print in order
line = "/r/{}{}| {}"
for item in actions:
    #make whitespace string based on subredding name length
    w=" "*(21-len(item[0]))
    print(line.format(item[0],w,str(item[1])))
