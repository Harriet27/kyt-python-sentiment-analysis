import json
import requests
from datetime import datetime
from transformers import pipeline
import pandas as pd
import os.path as ospath
import argparse

base_url = "http://localhost:3001"
uri = base_url + "/twitter/search-all/in_reply_to_status_id?id=448110947937165312&start_time=2014-03-08&end_time=2014-04-05"
response = requests.get(uri)
response_content = json.loads(response.content)
# print(response_content)

# time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# content_csv = pd.DataFrame(response_content)

# comments_arr = []
# for item in response_content:
#     comments_arr.append(item['text'])

# sentiment_classifier = pipeline('sentiment-analysis', model='finiteautomata/bertweet-base-sentiment-analysis')
# sentiment_analysis_result = sentiment_classifier(comments_arr)
# print(sentiment_analysis_result)

# sentiment_analysis_result_csv = pd.DataFrame(sentiment_analysis_result)

# data_csv = pd.concat([content_csv, sentiment_analysis_result_csv], axis=1)

# data_csv.to_csv(ospath.join('csv_files', f'data_csv_{time_now}.csv'), index = False)

def get_tweets(tweet_id, from_date, to_date):
    uri = base_url + f'/twitter/search-all/in_reply_to_status_id?id={tweet_id}&start_time={from_date}&end_time={to_date}'
    response = requests.get(uri)
    response_content = json.loads(response.content)
    return response_content


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tweet_id', type=str, help='The ID of the tweet.')
    parser.add_argument('from_date', type=str, help='Collect tweets starting from this date.')
    parser.add_argument('to_date', type=str, help='End collection of tweets on this date.')
    args = parser.parse_args()
    df = get_tweets(args.tweet_id, args.from_date, args.to_date)
    print(df)
