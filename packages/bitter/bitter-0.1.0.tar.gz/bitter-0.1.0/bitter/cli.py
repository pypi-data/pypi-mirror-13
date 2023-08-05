import click
import json

from bitter import utils

@click.group()
@click.option("--verbose", is_flag=True)
@click.option("--config", required=False)
@click.option('-c', '--credentials',show_default=True, default='credentials.json')
@click.pass_context
def main(ctx, verbose, config, credentials):
    ctx.obj = {}
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['CONFIG'] = config
    ctx.obj['CREDENTIALS'] = credentials

@main.command()
@click.option('--recursive', is_flag=True, help='Get following/follower/info recursively.', default=False)
@click.option('-u', '--user', default=None)
@click.option('-d', '--dburi',show_default=True, default=None)
@click.option('-n', '--name', show_default=True, default='extractor')
@click.option('-i', '--initfile', required=True, help='List of users to load')
@click.pass_context
def extract(ctx, recursive, user, dburi, name, initfile):
    print(locals())
    wq = utils.WorkerQueue.from_credentials(ctx.obj['CREDENTIALS'])
    utils.extract(wq,
                  recursive=recursive,
                  user=user,
                  dburi=dburi,
                  initfile=initfile,
                  extractor_name=name)


@main.group()
@click.pass_context 
def tweet(ctx):
    pass

@tweet.command('get')
@click.argument('tweetid')
@click.pass_context 
def get_tweet(ctx, tweetid):
    wq = utils.WorkerQueue.from_credentials(ctx.obj['CREDENTIALS'])
    c = wq.next()
    t = utils.get_tweet(c.client, tweetid)
    print(json.dumps(t, indent=2))
        

@tweet.command('search')
@click.argument('query')
@click.pass_context 
def get_tweet(ctx, query):
    wq = utils.WorkerQueue.from_credentials(ctx.obj['CREDENTIALS'])
    c = wq.next()
    t = utils.search_tweet(c.client, query)
    print(json.dumps(t, indent=2))

@main.group()
@click.pass_context
def users(ctx):
    pass

@users.command('get_one')
@click.argument('user')
@click.pass_context 
def get_user(ctx, user):
    wq = utils.WorkerQueue.from_credentials(ctx.obj['CREDENTIALS'])
    c = wq.next()
    u = utils.get_user(c.client, user)
    print(json.dumps(u, indent=2))

@users.command('get')
@click.argument('usersfile', 'File with a list of users to look up')
@click.pass_context
def get_users(ctx, usersfile):
    wq = utils.WorkerQueue.from_credentials(ctx.obj['CREDENTIALS'])
    with open(usersfile, 'r') as f:
        toadd = []
        for ix, line in enumerate(f):
            toadd.append(line.strip())
            if ix+1 % 1000 == 0:
                for user in utils.get_users(wq, toadd):
                    print(user)
                toadd = [] 
        if toadd:
            for user in utils.get_users(wq, toadd):
                print(user)
            

if __name__ == '__main__':
    main()
