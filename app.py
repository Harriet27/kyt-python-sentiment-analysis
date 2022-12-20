import json
import requests
from datetime import datetime
from transformers import pipeline
import pandas as pd
import os.path as ospath
import argparse
from flask import Flask, request, jsonify

app = Flask(__name__)

base_url = "http://localhost:3001"

def get_tweets(id, start_time, end_time):
    uri = base_url + f'/twitter/search-all/in_reply_to_status_id?id={id}&start_time={start_time}&end_time={end_time}'
    response = requests.get(uri)
    response_content = json.loads(response.content)
    return response_content

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('id', type=str, help='The ID of the tweet.')
#     parser.add_argument('start_time', type=str, help='Collect tweets starting from this date.')
#     parser.add_argument('end_time', type=str, help='End collection of tweets on this date.')
#     args = parser.parse_args()
#     df = get_tweets(args.id, args.start_time, args.end_time)

@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/get-comments", methods=["POST"])
def get_comments():
    input_json = request.get_json(force = True)
    body = {
        "id": input_json["id"],
        "start_time": input_json["start_time"],
        "end_time": input_json["end_time"],
    }
    data = get_tweets(body["id"], body["start_time"], body["end_time"])
    # create response data to DataFrame
    data_csv = pd.DataFrame(data)
    # create unique file name extension
    time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # extract comments only from list of dictionaries from api response
    comments_arr = []
    for item in data:
        comments_arr.append(item['text'])
    # do some sentiment analysis
    sentiment_classifier = pipeline('sentiment-analysis', model='finiteautomata/bertweet-base-sentiment-analysis')
    sentiment_analysis_result = sentiment_classifier(comments_arr)
    # create sentiment analysis data to DataFrame
    sentiment_analysis_result_csv = pd.DataFrame(sentiment_analysis_result)
    # combine 2 DataFrames into single CSV
    data_csv = pd.concat([data_csv, sentiment_analysis_result_csv], axis = 1)
    data_csv.to_csv(ospath.join('csv_files', f'data_csv_{time_now}.csv'), index = False)
    # concat 2 list of dictionaries
    result = []
    for index_a, item_a in enumerate(data):
        for index_b, item_b in enumerate(sentiment_analysis_result):
            merged_data = { **data[index_a], **sentiment_analysis_result[index_b] }
        result.append(merged_data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug = True)
