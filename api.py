import json
import requests
from datetime import datetime
from transformers import pipeline
import pandas as pd

base_url = "http://localhost:3001"
uri = base_url + "/twitter/search-all/in_reply_to_status_id?id=448110947937165312&start_time=2014-03-08&end_time=2014-04-05"
response = requests.get(uri)
response_content = json.loads(response.content)
print(response_content)

time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# convert array of dictionaries into csv file
content_csv = pd.DataFrame(response_content)
# content_csv.to_csv(f'response_content_{time_now}.csv', index=False)

comments_arr = []
for item in response_content:
    comments_arr.append(item['text'])

# zeroshot_classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
# candidate_labels = ('joy', 'happy', 'crash', 'crisis')

# zeroshot_classifier(result, candidate_labels)

sentiment_classifier = pipeline('sentiment-analysis', model='finiteautomata/bertweet-base-sentiment-analysis')
sentiment_analysis_result = sentiment_classifier(comments_arr)
print(sentiment_analysis_result)

sentiment_analysis_result_csv = pd.DataFrame(sentiment_analysis_result)
# sentiment_analysis_result_csv.to_csv(f'sentiment_analysis_result_{time_now}.csv', index=False)

# concat 2 csv into single csv fle
data_csv = pd.concat([content_csv, sentiment_analysis_result_csv], axis=1)
data_csv.to_csv(f'data_csv_{time_now}.csv', index=False)