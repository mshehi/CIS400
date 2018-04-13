# Megi Shehi
# CIS 400
# Assignment 2

import sys
import networkx as nx
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
import twitter
from functools import partial
from sys import maxint


#authorization for twitter
def oauth_login():

    CONSUMER_KEY = 'Ze2hvGchBKvNBsuVPgvdONg9c'
    CONSUMER_SECRET = 'hb7ipmbXRn2vQAY8i81T2Hw3PDsy98nm3p6QlAsyplkNhNpGj3'
    OAUTH_TOKEN = '954067729773887488-lzpFa4gbcMjYXISsH6wBlcFdeNICEMS'
    OAUTH_TOKEN_SECRET = 'QJANOlxpX4kwuREApTmmEW1Yf74pritiY0lPjV4pKLevS'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

#from twitter cookbook
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        # See https://dev.twitter.com/docs/error-codes-responses for common codes

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60 * 15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e  # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

#get friends and followers, from twitter cookbook
def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids,
                              count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids,
                                count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
        [get_friends_ids, friends_limit, friends_ids, "friends"],
        [get_followers_ids, followers_limit, followers_ids, "followers"]
    ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else:  # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids),
                                                                            label, (user_id or screen_name))

            # XXX: You may want to store data during each iteration to provide an
            # an additional layer of protection from exceptional circumstances

            if len(ids) >= limit or response is None:
                break

    return friends_ids[:friends_limit], followers_ids[:followers_limit]

#get user profile, from twitter cookbook
def get_user_profile(twitter_api, screen_names=None, user_ids=None):
    assert(screen_names != None) != (user_ids != None), \
        "Must have screen_names or user_ids, but not both"
    items_to_info = {}
    items = screen_names or user_ids

    while len(items) > 0:
        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup, screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup, user_id=items_str)

        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info
            else:  # user_ids
                items_to_info[user_info['id']] = user_info

    return items_to_info

#pretty print method
def pp(o):
    print json.dumps(o, indent=1)

#get top 5 most popular friends
def top5(friends):
    for z in friends:
        friends[z] = friends[z]['followers_count']
    friends = sorted(friends.iteritems(), reverse=True, key=lambda (k, v): (v, k))
    if (len(friends) >= 5):
        return friends[0:5]
    else:
        return friends[0:(len(friends))]

#create graph
G = nx.Graph()

#get twitter authorization
twitter_api = oauth_login()

#fetch first user to add node
user = get_user_profile(twitter_api, screen_names="joshfeinblatt")
user = user['a']["id"]
G.add_node(user)
print G.nodes()

#get friends and followers for user
friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
                                                       screen_name="joshfeinblatt",
                                                       friends_limit=5000,
                                                       followers_limit=5000)

#find reciprocal friends
reciprocal_friends_ids = list(set(friends_ids) & set(followers_ids))

#get user profiles for all reciprocal friends
user_followers = get_user_profile(twitter_api, user_ids=reciprocal_friends_ids)

followers = top5(user_followers)
G.add_nodes_from(x for (x,y) in followers)
G.add_edges_from((user,x) for x in followers)
pp(G.nodes())

#use ids of 5 most popular friends to crawl
for x,y in followers:
    #get friends and followers
    fr, fo = get_friends_followers_ids(twitter_api, user_id = x, friends_limit=100, followers_limit=100)
    response = list(set(fr) & set(fo))

    #get user profiles for reciprocal friends
    response = get_user_profile(twitter_api, user_ids=response)

    #get top 5 friends
    fids = top5(response)
    G.add_nodes_from(fids)
    G.add_edges_from((x,z) for z in fids)

    ids = next_queue = fids
    level = 1
    max_level = 5

    while level < max_level:
        level += 1
        (queue, next_queue) = (next_queue, [])

        for id in queue:
            fr, fo = get_friends_followers_ids(twitter_api, user_id=id, friends_limit=100, followers_limit=100)
            response = list(set(fr) & set(fo))
            response = get_user_profile(twitter_api, user_ids=response)
            fids = top5(response)
            pp(fids)
            G.add_nodes_from(fids)
            G.add_edges_from((id, z) for z in fids)
            next_queue += fids
    ids += next_queue

pp(G.nodes())

print G.number_of_nodes()
print G.number_of_edges()

#find diameter of graph
print G.diameter(G)

#find average shortest distance between nodes
print G.average_shortest_path_length(G)
