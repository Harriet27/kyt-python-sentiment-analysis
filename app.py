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
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug = True)

# command line > python app.py
# command line > python app.py 448110947937165312 2014-03-08 2014-04-05
