import tweepy
import pprint
import numpy as np
import dateparser
from sklearn.feature_extraction.text import TfidfVectorizer

consumer_key = "ZXirDbAP3IVKEREjpPeFWljMr"
consumer_secret = "2v72237kJoFcMnjwxpLkkTsvqZEAA1iYYTvsZJC4nAsPJvOifv"
access_key = "1093230584166563843-WuVa6oSp29Nu8u7asddseQ4JYsiNpw"
access_secret = "Aio0GXKhygws8RjYOllT9TPSaj06K8fD5r21DAEWd1L7D"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# test = 'tweets'
# test = 'pictures'
test = 'user'

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

elif test == 'user':
    max_tweets = 100
    display_tweets = 3
    user = None
    account = 'Google'
    topic = 'child'
    time = None
    time_limit = None
    if time is not None:
        time_limit = dateparser.parse(time)
    if account is not None:
        try:
            user = api.get_user(id=account)
        except 'Exception':
            user = None
    if user is not None:
        # valid user
        if topic is not None:
            # user-oriented search, with topic
            status_list = []
            text_list = []
            for status in tweepy.Cursor(api.user_timeline,
                                        id=account,
                                        count=max_tweets,
                                        exclude_replies=True,
                                        tweet_mode='extended',
                                        include_entities=True).items(max_tweets):
                if time_limit is not None:
                    if status.created_at > time_limit:
                        status_list.append(status)
                        text_list.append(status.full_text)
                else:
                    status_list.append(status)
                    text_list.append(status.full_text)

            text_list.insert(0, topic)
            vect_tweets = TfidfVectorizer(min_df=1).fit_transform(text_list)
            weights = np.array((vect_tweets * vect_tweets.T).A[0, 1:])
            rank = weights.argsort()[-display_tweets:][::-1]
            rank = rank[weights[rank] > 0]
            if len(rank) > 0:
                for i in rank:
                    print(status_list[i].user.screen_name)
                    print(status_list[i].created_at.ctime())
                    print(status_list[i].full_text)
                    if 'media' in status_list[i].entities:
                        for image in status_list[i].entities['media']:
                            image_url = image['media_url']
                            print(image_url)
            else:
                print('Sorry, no results found. Please tailor your keywords or time range.')

        if topic is None:
            # user-oriented search, without topic
            status_list = []
            actual_count = display_tweets
            if time_limit is not None:
                actual_count = max_tweets
            for status in tweepy.Cursor(api.user_timeline,
                                        id=account,
                                        count=actual_count,
                                        exclude_replies=True,
                                        tweet_mode='extended',
                                        include_entities=True).items(actual_count):
                if time_limit is not None:
                    if status.created_at > time_limit:
                        status_list.append(status)
                else:
                    status_list.append(status)
            for status in status_list:
                print(status.user.screen_name)
                print(status.created_at.ctime())
                print(status.full_text)
                if 'media' in status.entities:
                    for image in status.entities['media']:
                        image_url = image['media_url']
                        print(image_url)
    else:
        # no user, topic-oriented search
        if topic is not None:
            status_list = []
            actual_count = display_tweets
            if time_limit is not None:
                actual_count = max_tweets
            for status in tweepy.Cursor(api.search,
                                        q=topic,
                                        lang='en',
                                        count=actual_count,
                                        tweet_mode='extended',
                                        include_entities=True).items(actual_count):
                if time_limit is not None:
                    if status.created_at > time_limit:
                        status_list.append(status)
                else:
                    status_list.append(status)
            for status in status_list:
                print(status.user.screen_name)
                print(status.created_at.ctime())
                print(status.full_text)
                if 'media' in status.entities:
                    for image in status.entities['media']:
                        image_url = image['media_url']
                        print(image_url)

        else:  # if topic is None:
            print('Neither user nor topic is specified. Please specify at least one.')