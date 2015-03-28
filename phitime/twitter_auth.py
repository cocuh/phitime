from rauth import OAuth1Service


def gen_twitter_oauth_service(consumer_token, consumer_secret):
    twitter_service = OAuth1Service(
        consumer_key=consumer_token,
        consumer_secret=consumer_secret,
        name='twitter',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authorize',
        request_token_url='https://api.twitter.com/oauth/request_token',
        base_url='https://api.twitter.com/1.1/'
    )
    return twitter_service
