"""

This file creates an index in the elasticsearch from a config file.

"""

from json import load
from argparse import ArgumentParser
from elasticsearch import Elasticsearch

es = Elasticsearch('localhost:9200')


def delete_old_index(index):
    try:
        es.indices.delete(index=index, ignore=[400, 404])
    except Exception as e:
        print("[WARNING] some exception has occurred!", e)


def create_index(index, config):
    try:
        with open(config) as file:
            config = load(file)

        es.indices.create(index=index, body=config)
        print("[INFO] index " + index + " has been created!")
    except Exception as e:
        print("[WARNING] some exception has occurred!", e)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--index', required=True, help='name of the ES index')
    parser.add_argument('--config', required=True, help='path to the ES mapping config')
    args = parser.parse_args()
    delete_old_index(args.index)
    create_index(args.index, args.config)
