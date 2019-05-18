import tweepy
import pprint

consumer_key = "ZXirDbAP3IVKEREjpPeFWljMr"
consumer_secret = "2v72237kJoFcMnjwxpLkkTsvqZEAA1iYYTvsZJC4nAsPJvOifv"
access_key = "1093230584166563843-WuVa6oSp29Nu8u7asddseQ4JYsiNpw"
access_secret = "Aio0GXKhygws8RjYOllT9TPSaj06K8fD5r21DAEWd1L7D"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# test = 'tweets'
test = 'pictures'

topic = "dogs"
if test == 'tweets':
    max_tweets = 3
    all_tweets = []
    for text in tweepy.Cursor(api.search, q=topic, tweet_mode='extended').items(max_tweets):
        all_tweets.append(text.full_text)
    pprint.pprint(all_tweets)

elif test == 'pictures':
    pictures = tweepy.Cursor(api.search, q=topic, tweet_mode='extended', include_entities=True).items()
    for photo in pictures:
        media_files = []
        if 'media' in photo.entities:
            for image in photo.entities['media']:
                url_tweet = (image['media_url'])
                media_files.append(url_tweet)
        if len(media_files) > 0:
            break
    print(media_files[0])
