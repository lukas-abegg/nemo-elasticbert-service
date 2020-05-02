import json
from bs4 import BeautifulSoup
import urllib3
import numpy as np
import pandas as pd

import re

http = urllib3.PoolManager()

rows = 20


def get_data(start: int, rows: int):
    url = f"http://nemo-solrcloud-cluster1.springer-sbm.com:8983/solr/nemo_smed_live-2019-10-17-10/select?wt=json&q=*:*&fq=-productGroups:[*%20TO%20*]&fq=description:[*%20TO%20*]&fq=disciplinetaxonomyNames:Onkologie&fq=language:en&rows={rows}&start={start}"
    response = http.request('GET', url)
    return json.loads(response.data.decode('utf-8'))


_RE_COMBINE_WHITESPACE = re.compile(r"\s+")


def clean_text_from_html(raw_html: str) -> str:
    clean_text = BeautifulSoup(raw_html, 'html.parser').text
    clean_text.replace('\r', ' ').replace('\n', ' ')
    clean_text = _RE_COMBINE_WHITESPACE.sub(" ", clean_text).strip()
    return clean_text


def get_document_data(document):
    doc_id = document['id']
    doc_title = clean_text_from_html(document['title'])
    doc_abstract = clean_text_from_html(document['description'])
    return [doc_id, doc_title, doc_abstract]


export_folder = "../exported_data/"
filename_csv = export_folder + "smed_onko_articles.csv"


def create_csv(data):
    arr = np.asarray(data)
    df = pd.DataFrame(data=arr, columns=['id', 'title', 'abstract'])
    df.to_csv(filename_csv, index=False)
    print(filename_csv, "is created")


data = get_data(0, 0)
numFound = data['response']['numFound']
print(numFound, "documents found.")

articles = []

start = 0
for i in range(0, numFound, rows):
    print(f"Get documents {start + 1} to {start + rows}")
    data = get_data(start, rows)

    for document in data['response']['docs']:
        articles.append(get_document_data(document))

    start = start + rows

create_csv(articles)

print(len(articles) - 1, " articles were exported to ", filename_csv)
