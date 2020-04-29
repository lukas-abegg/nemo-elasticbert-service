import os
from pprint import pprint

from flask import Flask, render_template, jsonify, request
from bert_serving.client import BertClient
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError

SEARCH_SIZE = 20
INDEX_NAME = os.environ['INDEX_NAME']
app = Flask(__name__)

bc = BertClient(ip='localhost', output_fmt='list', check_length=False)
client = Elasticsearch('localhost:9200')


@app.route('/')
def index():
    return render_template('index.html')


def word_search(query):
    return {
        "multi_match": {
            "query": query,
            "fields": ["title", "abstract"]
        }
    }


def vector_search(query, query_vector):

    return {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^0.01", "abstract^0.01"]
                }
            },
            "functions": [
                {
                    "script_score": {
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, doc['abstract_vector'])+2",
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                {
                    "script_score": {
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, doc['title_vector'])+2",
                            "params": {"query_vector": query_vector}
                        }
                    }
                }
            ],
            "boost_mode": "sum"
        }
    }


@app.route('/search')
def analyzer():
    query = request.args.get('q')
    mode = request.args.get('mode')

    query_vector = bc.encode([query])[0]
    pprint(query)

    if mode == "vec":
        request_elastic = vector_search(query, query_vector)
    else:
        request_elastic = word_search(query)

    try:
        response = client.search(
            index='mpedia',  # name of the index
            body={
                "size": SEARCH_SIZE,
                "query": request_elastic,
                "_source": {"includes": ["id", "title", "abstract"]}
            }
        )
    except ConnectionError:
        print("[WARNING] docker isn't up and running!")
    except NotFoundError:
        print("[WARNING] no such index!")

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
