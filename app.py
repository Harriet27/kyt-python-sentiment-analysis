import json
import requests
from datetime import datetime
from transformers import pipeline
import pandas as pd
import os.path as ospath
from flask import Flask, request, jsonify
from time import sleep

app = Flask(__name__)

base_url = "http://localhost:3001"

'''
This is to set function to hit JS API
'''
def get_tweet_list(user, maxResults, fromYear, fromMonth, fromDate, toYear, toMonth, toDate):
    uri = base_url + '/twitter/full-archive-search'
    body = {
        "user": user,
        "maxResults": maxResults,
        "fromYear": fromYear,
        "fromMonth": fromMonth,
        "fromDate": fromDate,
        "toYear": toYear,
        "toMonth": toMonth,
        "toDate": toDate,
    }
    response = requests.post(uri, json = body)
    response_content = json.loads(response.content)
    return response_content["result"]

def get_comments(id, start_time, end_time):
    uri = base_url + f'/twitter/search-all/in_reply_to_status_id?id={id}&start_time={start_time}&end_time={end_time}'
    response = requests.get(uri)
    response_content = json.loads(response.content)
    return response_content

'''
Python API Router
'''
@app.route("/")
def hello_world():
    return "Hi there! Python API is working!"

@app.route("/get-searched-tweets-list", methods=["POST"])
def get_searched_tweets_list():
    input_json = request.get_json()
    body = {
        "user": input_json["user"],
        "maxResults": input_json["maxResults"],
        "fromDate": input_json["fromDate"],
        "fromMonth": input_json["fromMonth"],
        "fromYear": input_json["fromYear"],
        "toDate": input_json["toDate"],
        "toMonth": input_json["toMonth"],
        "toYear": input_json["toYear"],
    }
    data = get_tweet_list(body["user"], body["maxResults"], body["fromYear"], body["fromMonth"], body["fromDate"], body["toYear"], body["toMonth"], body["toDate"])
    # create response data to DataFrame
    data_csv = pd.DataFrame(data)
    # extract DataFrame to csv file
    filename = f'{body["user"]}_tweets_list_{body["fromDate"] + "-" + body["fromMonth"] + "-" + body["fromYear"]}_{body["toDate"] + "-" + body["toMonth"] + "-" + body["toYear"]}.csv'
    data_csv.to_csv(ospath.join('csv_files/searched_tweets_list', filename), index = False)
    return [d['tweet_id'] for d in data]

@app.route("/get-comments-analised", methods=["POST"])
def get_comments_analised():
    input_json = request.get_json()
    body = {
        "id": input_json["id"],
        "start_time": input_json["start_time"],
        "end_time": input_json["end_time"],
    }
    data = get_comments(body["id"], body["start_time"], body["end_time"])
    if data["message"] == "Comments found!":
        # create response data to DataFrame
        data_result = data["result"]
        data_csv = pd.DataFrame(data_result)
        # extract comments only from list of dictionaries from api response
        comments_arr = []
        for item in data_result:
            comments_arr.append(item['text'])
        # do some sentiment analysis
        sentiment_classifier = pipeline('sentiment-analysis', model='finiteautomata/bertweet-base-sentiment-analysis')
        sentiment_analysis_result = sentiment_classifier(comments_arr)
        # create sentiment analysis data to DataFrame
        sentiment_analysis_result_csv = pd.DataFrame(sentiment_analysis_result)
        # combine 2 DataFrames into single CSV
        data_csv = pd.concat([data_csv, sentiment_analysis_result_csv], axis = 1)
        filename = f'{body["id"]}_comments_analised_{body["start_time"]}_{body["end_time"]}.csv'
        data_csv.to_csv(ospath.join('csv_files/tweet_comments', filename), index = False)
        # concat 2 list of dictionaries
        result = []
        for index_a, item_a in enumerate(data_result):
            for index_b, item_b in enumerate(sentiment_analysis_result):
                merged_data = { **data_result[index_a], **sentiment_analysis_result[index_b] }
            result.append(merged_data)
        # return jsonify(result)
        return jsonify({
            "count": len(result),
            "result": result,
        })
    elif data["message"] == "No comments found!":
        noCommentResponse = [{
            "message": "No comments found",
        }]
        noCommentResponse_csv = pd.DataFrame(noCommentResponse)
        filenameNoComments = f'{body["id"]}_comments_analised_{body["start_time"]}_{body["end_time"]}.csv'
        noCommentResponse_csv.to_csv(ospath.join('csv_files/tweet_comments', filenameNoComments), index = False)
        return jsonify({
            "message": "No comments found",
        })

@app.route("/get-comments-analised-bulk", methods=["POST"])
def get_comments_analised_bulk():
    input_json = request.get_json()
    body = {
        "id": input_json["id"], # array of tweet_id
        "start_time": input_json["start_time"], # string for start_time (yyyy-mm-dd)
        "end_time": input_json["end_time"], # string for end_time (yyyy-mm-dd)
    }
    result = []
    for val in body["id"]:
        data = get_comments(val, body["start_time"], body["end_time"])
        if data["message"] == "Comments found!":
            print(f'ONGOING FOR ID: {val}')
            # create response data to DataFrame
            data_result = data["result"]
            data_csv = pd.DataFrame(data_result)
            # extract comments only from list of dictionaries from api response
            comments_arr = []
            for item in data_result:
                comments_arr.append(item['text'])
            # do some sentiment analysis
            sentiment_classifier = pipeline('sentiment-analysis', model='finiteautomata/bertweet-base-sentiment-analysis')
            sentiment_analysis_result = sentiment_classifier(comments_arr)
            # create sentiment analysis data to DataFrame
            sentiment_analysis_result_csv = pd.DataFrame(sentiment_analysis_result)
            # combine 2 DataFrames into single CSV
            data_csv = pd.concat([data_csv, sentiment_analysis_result_csv], axis = 1)
            filename = f'{val}_comments_analised_{body["start_time"]}_{body["end_time"]}.csv'
            data_csv.to_csv(ospath.join('csv_files/bulk_tweet_comments', filename), index = False)
            # concat 2 list of dictionaries
            for index_a, item_a in enumerate(data_result):
                for index_b, item_b in enumerate(sentiment_analysis_result):
                    merged_data = { **data_result[index_a], **sentiment_analysis_result[index_b] }
                result.append(merged_data)
            # return jsonify({
            #     "count": len(result),
            #     "result": result,
            # })
            print(f'> PROCESS DONE FOR ID: {val}')
            sleep(1.75)
        elif data["message"] == "No comments found!":
            print(f'ONGOING FOR ID: {val}')
            noCommentResponse = [{
                "message": "No comments found",
            }]
            noCommentResponse_csv = pd.DataFrame(noCommentResponse)
            filenameNoComments = f'{val}_comments_analised_{body["start_time"]}_{body["end_time"]}.csv'
            noCommentResponse_csv.to_csv(ospath.join('csv_files/bulk_tweet_comments', filenameNoComments), index = False)
            # return jsonify({
            #     "message": "No comments found",
            # })
            print(f'> PROCESS DONE FOR ID: {val}')
            sleep(1.75)
    return jsonify({
        "message": "Analysis finished!",
    })

@app.route("/download")
def download():
    url = "https://qubeshub.org/publications/1220/serve/1/3861?el=1&download=1"
    r = requests.get(url)
    filename = r.headers["Content-Disposition"].split('"')[1]
    with open(filename, "wb") as f_out:
        print(f"Downloading {filename}")
        return f_out.write(r.content)

if __name__ == "__main__":
    app.run(port = 8000, debug = True)
