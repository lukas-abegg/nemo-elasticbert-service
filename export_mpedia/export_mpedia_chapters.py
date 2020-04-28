import json
from bs4 import BeautifulSoup
import urllib3
import numpy as np

http = urllib3.PoolManager()

rows = 20


def get_data(start: int, rows: int):
    url = f"http://nemo-solrcloud-qa.springer-sbm.com:8983/solr/nemo_mpedia_fulltext-2020-04-27-17-09-46-192/select?q=*:*&wt=json&rows={rows}&start={start}"
    response = http.request('GET', url)
    return json.loads(response.data.decode('utf-8'))


def clean_text_from_html(raw_html: str) -> str:
    return BeautifulSoup(raw_html, 'html.parser').text


def get_document_data(document):
    doc_id = document['id']
    doc_title = clean_text_from_html(document['titleHtml'])
    doc_abstract = clean_text_from_html(document['abstractHtml'])
    return [f'"{doc_id}"', f'"{doc_title}"', f'"{doc_abstract}"']


export_folder = "../exported_data/"
filename_csv = export_folder + "mpedia_chapters.csv"


def create_csv(data):
    arr = np.asarray(data)
    np.savetxt(filename_csv, arr, fmt='%s', delimiter=",")
    print(filename_csv, "is created")


data = get_data(0, 0)
numFound = data['response']['numFound']
print(numFound, "documents found.")

chapters = [['"id"', '"title"', '"abstract"']]

start = 0
for i in range(0, numFound, rows):
    print(f"Get documents {start + 1} to {start + rows}")
    data = get_data(start, rows)

    for document in data['response']['docs']:
        chapters.append(get_document_data(document))

    start = start + rows

create_csv(chapters)

print(len(chapters) - 1, " chapters were exported to ", filename_csv)
