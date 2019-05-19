
## fallback
- utter_default

## greeting path 1
* greet
- utter_greet

## fine path 1
* fine_normal
- utter_help

## fine path 2
* fine_ask
- utter_reply

## tweets path text
* tweet_search
- utter_search_light
- action_get_tweets
- slot{"account": null, "topic": null, "content": null, "time": null}

## tweets path time range
* tweet_search{"time": "3 weeks"}
- utter_search_heavy
- action_get_tweets
- slot{"account": null, "topic": null, "content": null, "time": null}

## tweets path pictures
* tweet_search{"content": "pictures"}
- utter_search_heavy
- action_get_tweets
- slot{"account": null, "topic": null, "content": null, "time": null}

## thanks path 1
* thanks
- utter_anything_else

## bye path 1
* bye
- utter_bye