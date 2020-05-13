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


def word_search(query, boost_title: int, boost_abstract: int):
    return {
        "multi_match": {
            "query": query,
            "fields": [
                f"title^{boost_title}",
                f"title.edge_ngram^{float(boost_title / 2)}",
                f"title.ngram^{float(boost_title / 4)}",
                f"abstract^{boost_abstract}",
                f"abstract.edge_ngram^{float(boost_title / 2)}",
                f"abstract.ngram^{float(boost_title / 4)}"
            ]
        }
    }


def vector_search(query, query_vector, boost_title: int, boost_abstract: int, boost_vec_title: int, boost_vec_abstract: int):
    return {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    f"title^{boost_title}",
                                    f"title.edge_ngram^{float(boost_title / 2)}",
                                    f"title.ngram^{float(boost_title / 4)}",
                                    f"abstract^{boost_abstract}",
                                    f"abstract.edge_ngram^{float(boost_title / 2)}",
                                    f"abstract.ngram^{float(boost_title / 4)}"
                                ]
                            }
                        }
                    ]
                }
            },
            "functions": [
                {
                    "script_score": {
                        "script": {
                            "source": "(cosineSimilarity(params.query_vector, doc['abstract_vector'])+ 1.0)*params.boost_vec",
                            "params": {"query_vector": query_vector, "boost_vec": boost_vec_title}
                        }
                    }
                },
                {
                    "script_score": {
                        "script": {
                            "source": "(cosineSimilarity(params.query_vector, doc['title_vector'])+ 1.0)*params.boost_vec",
                            "params": {"query_vector": query_vector, "boost_vec": boost_vec_abstract}
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
    boost_title = int(request.args.get('boost_title'))
    boost_abstract = int(request.args.get('boost_abstract'))
    boost_vec_title = int(request.args.get('boost_vec_title'))
    boost_vec_abstract = int(request.args.get('boost_vec_abstract'))
    mode = request.args.get('mode')

    query_vector = bc.encode([query])[0]
    pprint(query)

    if mode == "vec":
        request_elastic = vector_search(query, query_vector, boost_title,
                                        boost_abstract, boost_vec_title, boost_vec_abstract)
    else:
        request_elastic = word_search(query, boost_title, boost_abstract)

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
