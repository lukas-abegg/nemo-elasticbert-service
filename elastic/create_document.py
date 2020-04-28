"""

This script creates documents in the required format for
indexing.

"""
import os

import json
from pandas import read_csv
from argparse import ArgumentParser
from bert_serving.client import BertClient

bc = BertClient(output_fmt='list', check_length=False)


def create_document(doc, embs, index_name):
    return {
        '_op_type': 'index',
        '_index': index_name,
        'id': doc['id'],
        'title': doc['title'],
        'abstract': doc['abstract'],
        'title_vector': embs[0],
        'abstract_vector': embs[1]
    }


def load_dataset(path):
    docs = []
    df = read_csv(path, escapechar='\\')
    for row in df.iterrows():
        series = row[1]
        doc = {
            'id': series.id,
            'title': series.title,
            'abstract': series.abstract
        }
        docs.append(doc)
    return docs


def bulk_write_to_json(output_file: str, index: str, docs, vecs):
    with open(output_file, mode='a', encoding='utf-8') as f:
        for doc, embs in zip(docs, vecs):
            d = create_document(doc, embs, index)
            f.write(json.dumps(d) + '\n')


def predict_vecs_and_write_to_json(output_file: str, index: str, docs, batch_size=50):
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i: i + batch_size]

        embeddings_titles = bc.encode([doc['title'] for doc in batch_docs])
        embeddings_abstracts = bc.encode([doc['abstract'] for doc in batch_docs])

        embeddings = [[embeddings_titles[j], embeddings_abstracts[j]] for j in range(0, len(embeddings_titles))]

        print(f"[INFO] Write document {i} up to {i+batch_size} into json {output_file}")
        bulk_write_to_json(output_file, index, batch_docs, embeddings)
        print(f"[INFO] Bulk writing done!")


def delete_old_json(json_file):
    if os.path.exists(json_file):
        os.remove(json_file)
    else:
        print("The file does not exist")


def main(args):
    delete_old_json(args.output)
    docs = load_dataset(args.csv)
    predict_vecs_and_write_to_json(args.output, args.index, docs)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--index', required=True, help='name of the ES index')
    parser.add_argument('--csv', required=True, help='path to the input csv file')
    parser.add_argument('--output', required=True, help='name of the output file (example.json1)')
    args = parser.parse_args()
    main(args)
