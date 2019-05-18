# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json
from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
import tweepy 		#https://github.com/tweepy/tweepy
import sys
import csv
import re

logger = logging.getLogger(__name__)

#Twitter API credentials
consumer_key = "ZXirDbAP3IVKEREjpPeFWljMr"
consumer_secret = "2v72237kJoFcMnjwxpLkkTsvqZEAA1iYYTvsZJC4nAsPJvOifv"
access_key = "1093230584166563843-WuVa6oSp29Nu8u7asddseQ4JYsiNpw"
access_secret = "Aio0GXKhygws8RjYOllT9TPSaj06K8fD5r21DAEWd1L7D"


class ActionJoke(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_joke"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(
            requests.get("https://api.chucknorris.io/jokes/random").text
        )  # make an api call
        joke = request["value"]  # extract a joke from returned json response
        dispatcher.utter_message(joke)  # send the message back to the user
        return []

class ActionGetTweets(Action):

    def name(self):
        return "action_get_tweets"

    def run(self, dispatcher, tracker, domain):
        #--- authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        content = tracker.get_slot('content')
        picture_list = ['pictures', 'picture', 'images', 'image', 'photos', 'photo']
        if (content is not None) and any(content in keyword for keyword in picture_list):
            self.get_pictures(api, dispatcher, tracker, domain)
        else:
            self.get_tweets(api, dispatcher, tracker, domain)

    def get_tweets(self, api, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')  # TODO: include other entities
        max_tweets = 3
        all_tweets = []

        for text in tweepy.Cursor(api.search, q=topic, tweet_mode='extended').items(max_tweets):
            all_tweets.append(text.full_text)
        for tweet in all_tweets:
            dispatcher.utter_message(tweet)

    def get_pictures(self, api, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')  # TODO: include other entities
        pictures = tweepy.Cursor(api.search, q=topic, tweet_mode='extended', include_entities=True).items()
        for photo in pictures:
            media_files = []
            if 'media' in photo.entities:
                for image in photo.entities['media']:
                    url_tweet = (image['media_url'])
                    media_files.append(url_tweet)
            if len(media_files) > 0:
                break
        dispatcher.utter_attachment(media_files[0])
