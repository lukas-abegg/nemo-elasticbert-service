from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
from bert_serving.client import BertClient

# total number of responses
SEARCH_SIZE = 10

# establishing connections
bc = BertClient(ip='localhost', output_fmt='list', check_length=False)
client = Elasticsearch('localhost:9200')

# this query is used as the search term, feel free to change
query = 'morbus'
query_vector = bc.encode([query])[0]

script_query = {
    "function_score": {
        "query": {"match_all": {}},
        "functions": [
            {
                "script_score": {
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, doc['abstract_vector']) + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            {
                "script_score": {
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, doc['title_vector'])",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        ],
        "boost_mode": "sum"
    }
}

try:
    response = client.search(
         index='mpedia',  # name of the index
         body={
             "size": SEARCH_SIZE,
             "query": script_query,
             "_source": {"includes": ["id", "title", "abstract"]}
         }
     )
    print(response)
except ConnectionError:
    print("[WARNING] docker isn't up and running!")
except NotFoundError:
    print("[WARNING] no such index!")
