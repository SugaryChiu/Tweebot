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
import numpy as np
import dateparser
from sklearn.feature_extraction.text import TfidfVectorizer
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

        # if tracker.get_slot('account') is not None:
        #     print('account:' + tracker.get_slot('account'))
        # if tracker.get_slot('time') is not None:
        #     print('time:' + tracker.get_slot('time'))
        # if tracker.get_slot('topic') is not None:
        #     print('topic:' + tracker.get_slot('topic'))
        # if tracker.get_slot('content') is not None:
        #     print('content:' + tracker.get_slot('content'))

        return [SlotSet('account', None),
                SlotSet('time', None),
                SlotSet('topic', None),
                SlotSet('content', None)]

    def get_tweets(self, api, dispatcher, tracker, domain):
        max_tweets = 100
        display_tweets = 3
        account = tracker.get_slot('account')
        topic = tracker.get_slot('topic')
        time = tracker.get_slot('time')
        user = None
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
                        dispatcher.utter_message(status_list[i].user.screen_name)
                        dispatcher.utter_message(status_list[i].created_at.ctime())
                        dispatcher.utter_message(status_list[i].full_text)
                        if 'media' in status_list[i].entities:
                            for image in status_list[i].entities['media']:
                                image_url = image['media_url']
                                dispatcher.utter_attachment(image_url)
                else:
                    dispatcher.utter_message('Sorry, no results found. Please tailor your keywords or time range.')

            else:  # if topic is None
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
                    dispatcher.utter_message(status.user.screen_name)
                    dispatcher.utter_message(status.created_at.ctime())
                    dispatcher.utter_message(status.full_text)
                    if 'media' in status.entities:
                        for image in status.entities['media']:
                            image_url = image['media_url']
                            dispatcher.utter_attachment(image_url)
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
                    dispatcher.utter_message(status.user.screen_name)
                    dispatcher.utter_message(status.created_at.ctime())
                    dispatcher.utter_message(status.full_text)
                    if 'media' in status.entities:
                        for image in status.entities['media']:
                            image_url = image['media_url']
                            dispatcher.utter_attachment(image_url)

            else:  # if topic is None:
                dispatcher.utter_template('utter_no_user_topic')

    def get_pictures(self, api, dispatcher, tracker, domain):
        display_count = 0
        topic = tracker.get_slot('topic')
        if topic is not None:
            for status in tweepy.Cursor(api.search,
                                        q=topic,
                                        tweet_mode='extended',
                                        include_entities=True).items():
                if 'media' in status.entities:
                    for image in status.entities['media']:
                        image_url = image['media_url']
                        dispatcher.utter_attachment(image_url)
                        display_count += 1
                    break
            if display_count == 0:
                dispatcher.utter_message('No pictures found. Please change keyword or search again.')
        else:  # no topic for picture
            dispatcher.utter_message('No keyword specified for picture search.')
