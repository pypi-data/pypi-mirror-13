import logging
import time

from collections import defaultdict, Counter
from time import sleep
import signal
import dataset
import sys
import sqlalchemy
import json

from twitter import *
from collections import OrderedDict
from itertools import islice

logger = logging.getLogger(__name__)


class AttrToFunc(object):
    def __init__(self, uriparts=None, handler=None):
        if uriparts:
            self.__uriparts = uriparts
        else:
            self.__uriparts = []
        #self.__uriparts = []
        self.handler = handler

    def __getattr__(self, k):
        def extend_call(arg):
            return AttrToFunc(
                uriparts=self.__uriparts + [arg,],
                handler=self.handler)
        if k == "_":
            return extend_call
        else:
            return extend_call(k)

    def __call__(self, *args, **kwargs):
        # for i, a in enumerate(args)e
        #     kwargs[i] = a
        return self.handler(self.__uriparts, *args, **kwargs)

class Worker(object):
    def __init__(self, name, client):
        self.name = name
        self.client = client
        self.throttled_time = False

    @property
    def throttled(self):
        if not self.throttled_time:
            return False
        t = time.time()
        delta = self.throttled_time - t
        if delta > 0:
            logger.info("Worker %s throttled for %s seconds" % (self.name, delta))
            return True
        return False

    def throttle_until(self, epoch=None):
        self.throttled_time = int(epoch)


class WorkerQueue(AttrToFunc):
    def __init__(self, wait=True):
        self.queue = set()
        self.index = 0
        self.wait = wait
        AttrToFunc.__init__(self, handler=self.handle_call)

    def ready(self, worker):
        self.queue.add(worker)

    def handle_call(self, uriparts, *args, **kwargs):
        logging.info('Called: {}'.format(uriparts))
        logging.info('With: {} {}'.format(args, kwargs))
        while True:
            try:
                c = self.next()
                logging.info('Next: {}'.format(c.name))
                resp = getattr(c.client, "/".join(uriparts))(*args, **kwargs)
                return resp
            except TwitterHTTPError as ex:
                if ex.e.code in (429, 502, 503, 504):
                    limit = ex.e.headers.get('X-Rate-Limit-Reset', time.time() + 30)
                    logging.info('{} limited'.format(c.name))
                    c.throttle_until(limit)
                    continue

    @property
    def client(self):
        return self.next().client

    @classmethod
    def from_credentials(self, cred_file):
        wq = WorkerQueue()

        with open(cred_file) as f:
            for line in f:
                cred = json.loads(line)
                c = Twitter(auth=OAuth(cred['token_key'],
                                       cred['token_secret'],
                                       cred['consumer_key'],
                                       cred['consumer_secret']))
                wq.ready(Worker(cred["user"], c))
        return wq

    def _next(self):
        for worker in self.queue:
            if not worker.throttled:
                return worker
        raise Exception('No worker is available')

    def next(self):
        if not self.wait:
            return self._next()
        while True:
            try:
                return self._next()
            except Exception:
                first_worker = min(self.queue, key=lambda x: x.throttled_time)
                diff = first_worker.throttled_time - time.time()
                logger.info("All workers are busy. Waiting %s seconds" % diff)
                sleep(diff)


def signal_handler(signal, frame):
    logger.info('You pressed Ctrl+C!')
    sys.exit(0)


def get_users(wq, ulist, by_name=False, max_users=100):
    t = 'name' if by_name else 'uid'
    logger.info('Getting users by {}: {}'.format(t, ulist))
    ilist = iter(ulist)
    while True:
        userslice = ",".join(islice(ilist, max_users))
        if not userslice:
            break
        if by_name:
            resp = wq.users.lookup(screen_name=userslice)
        else:
            resp = wq.users.lookup(user_id=userslice)
        for user in resp:
            uid = user['id']
            if 'status' in user:
                del user['status'] 
            ts = time.strftime('%s', time.strptime(user['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            user['created_at_stamp'] = ts
            del user['created_at']
            user['pending'] = True
            user['cursor'] = -1
            yield user


# TODO: Move error handling to the worker queue
def extract(wq, recursive=False, user=None, initfile=None, dburi=None, extractor_name=None):
    signal.signal(signal.SIGINT, signal_handler)
    
    w = wq.next()
    if not dburi:
        dburi = 'sqlite:///%s.db' % extractor_name

    db = dataset.connect(dburi)

    cursors = db.get_table('cursors')
    followers = db.get_table('followers')
    followers.create_column('isfollowed', sqlalchemy.types.Integer)
    followers.create_column('follower', sqlalchemy.types.Integer)
    followers.create_index(['isfollowed', 'follower'])

    users = db.get_table('users', primary_id='uid', primary_type='Integer')
    users.create_column('cursor', sqlalchemy.types.Integer)
    users.create_column('pending', sqlalchemy.types.Boolean)
    users.create_column('followers_count', sqlalchemy.types.Integer)
    users.create_column('injson', sqlalchemy.types.String)

    if not users.count(pending=True):
        screen_names = []
        user_ids = []
        if not user:
            logger.info("No user. I will open %s" % initfile)
            with open(initfile, 'r') as f:
                for line in f:
                    user = line.strip().split(',')[0]
                    try:
                        int(user)
                        user_ids.append(user)
                    except ValueError:
                        screen_names.append(user.split('@')[-1])
        else:
            try:
                user_ids.append(int(user))
                logger.info("Added id")
            except Exception as ex:
                logger.info("Exception: {}".format(ex))
                logger.info("Added screen_name")
                screen_names.append(user)
        nusers = list(get_users(w.client, screen_names, by_name=True))
        if user_ids:
            nusers += list(get_users(w.client, user_ids, by_name=False))
        for i in nusers:
            users.upsert(i, keys=['uid'])

    total_users = users.count(pending=True)

    while users.count(pending=True) > 1:
        w = wq.next()
        logger.info("Using account: %s" % w.name)
        candidate = users.find_one(pending=True, order_by='followers_count')
        if not candidate:
            break
        pending = True
        cursor = candidate.get('cursor', -1)
        uid = candidate['uid']

        logger.info("#"*20)
        logger.info("Getting %s" % uid)
        logger.info("Cursor %s" % cursor)
        logger.info("Pending: %s/%s" % (users.count(pending=True), total_users))
        try:
            resp = w.client.followers.ids(user_id=uid, cursor=cursor)
        except TwitterHTTPError as ex:
            if ex.e.code in (429, 502, 503, 504):
                limit = ex.e.headers.get('X-Rate-Limit-Reset', time.time() + 30)
                w.throttle_until(limit)
                continue
        if 'ids' in resp:
            logger.info("New followers: %s" % len(resp['ids']))
            temp = []
            for i in resp['ids']:
                temp.append(dict(isfollowed=uid,
                                    follower=i))
            followers.insert_many(temp)
            total_followers = candidate['followers_count']
            fetched_followers = followers.count(isfollowed=uid)
            logger.info("Fetched: %s/%s followers" % (fetched_followers,
                                                total_followers))
            cursor = resp["next_cursor"]
            if cursor > 0:
                pending = True
                logger.info("Getting more followers for %s" % uid)
            else:
                cursor = -1
                pending = False
        else:
            logger.info("Error with id %s %s" % (uid, resp))
            pending = False

        users.upsert(dict(uid=uid,
                        pending=pending,
                        cursor=cursor),
                    keys=['uid'])
        sys.stdout.flush()


def get_tweet(c, tid):
    return c.statuses.show(id=tid)

def search_tweet(c, query):
    return c.search.tweets(q=query)

def get_user(c, user):
    try:
        int(user)
        return c.users.lookup(user_id=user)
    except ValueError:
        return c.users.lookup(screen_name=user)
