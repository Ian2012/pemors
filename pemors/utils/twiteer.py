import environ
import tweepy
from allauth.socialaccount.models import SocialAccount

from pemors.users.models import Status

env = environ.Env()


def get_user_tweets(user):
    if user and not SocialAccount.objects.filter(user=user).exists():
        return []

    social_account = SocialAccount.objects.get(user=user)
    client = tweepy.Client(bearer_token=env("TWITTER_BEARER_TOKEN"))
    response = client.get_users_tweets(
        id=social_account.uid, max_results=100, tweet_fields=[""]
    )
    for tweet in response.data:
        Status.objects.create(user=user, value=tweet)
    return response.data
