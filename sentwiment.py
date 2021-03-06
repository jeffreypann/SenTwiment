import tweepy
from textblob import TextBlob
import os
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', None)
GIPHY_TOKEN = os.environ.get('GIPHY_TOKEN', None)
TWEET_COUNT = 200
DECAY_RATE = (1-(1-7))  # 0.86
TIME_INTERVAL = 86400  # 1 day in seconds


def twitter_setup():
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
    twitter = tweepy.API(auth)
    return twitter


def get_Mood(sent):
    if sent >= 0.05:
        return 1
    elif sent <= -0.05:
        return -1
    else:
        return 0


def sentiment(tweets):
    final_sent = 0
    final_weight = 0
    time_curr = datetime.datetime.now()
    data = {}
    data['sentiment'] = 0
    data['tweets'] = []
    vader = SentimentIntensityAnalyzer()
    for tweet in tweets[:TWEET_COUNT]:
        time_created = tweet.created_at
        time_diff = (time_curr - time_created).total_seconds()
        if time_diff/TIME_INTERVAL <= 60:
            weight = DECAY_RATE**(time_diff/TIME_INTERVAL) # More recent -> greater weight (0.86 ^ (Δt / 1day))
        else:
            weight = DECAY_RATE** 60
        vader_pol = vader.polarity_scores(tweet.full_text)['compound']
        blob_pol = TextBlob(tweet.full_text).sentiment.polarity # 2 opinions are better than 1 !!
        sent = (vader_pol + blob_pol) / 2.0
        data['tweets'].append({"message": tweet.full_text, "sentiment": sent, "mood": get_Mood(sent)})
        sent *= weight
        final_sent += sent
        final_weight += weight
    data['sentiment'] = final_sent/final_weight
    return data


def get_tweets(user, twitter):
    tweets = twitter.user_timeline(screen_name=user,tweet_mode="extended")
    return tweets


def get_gif(user):
    url = "https://api.giphy.com/v1/gifs/search"
    name = "+".join(user.split())
    params = {
        "api_key": GIPHY_TOKEN,
        "q": name,
        "limit": "1"
    }
    r = requests.get(url,params=params)
    try:
        gif = r.json()['data'][0]['embed_url']
        return gif
    except:
        gif = "https://giphy.com/embed/v0eHX3n28wvoQ"
        return gif


twitter = twitter_setup()
vader = SentimentIntensityAnalyzer()