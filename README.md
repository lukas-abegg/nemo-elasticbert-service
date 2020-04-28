# elasticbert

This is a simple Information Retrieval system using pretrained BERT model and elasticsearch. 
We convert text into a fixed length vector which is then saved into an elasticsearch index. 
Then we use cosine similarity metric to figure out the most similar content out of the index. 
This is the overall workflow of the system.

### 1. Download pre - trained BERT models.

English
```bash
$ wget https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip
$ unzip cased_L-12_H-768_A-12.zip
$ cp cased_L-12_H-768_A-12 bert/models/
```
German
```bash
$ wget https://int-deepset-models-bert.s3.eu-central-1.amazonaws.com/tensorflow/bert-base-german-cased.zip
$ unzip bert-base-german-cased.zip
$ cp bert-base-german-cased bert/models/
```

### 2. Set environment variables
You need to set a pretrained BERT model and Elasticsearch's index name as environment variables:
```bash
$ export PATH_MODEL=./bert/model/bert-base-german-cased
$ export INDEX_NAME=mpedia
```
### 3.Run Docker containers
 ```bash
$ docker-compose up
```
To rebuild the image, simply run
 ```bash
$ docker-compose up --build
```
**CAUTION**: If possible, assign high memory(more than 8GB) to Docker's memory configuration because BERT container needs high memory.
### 4. Check Docker containers are running
 ```bash
$ docker ps
```
### 5. Install dependencies.
```bash
pip install argparse 
pip install elasticsearch 
pip install bert-serving-client
```
### 6. Create elasticsearch index
```bash
python3 elastic/create_index.py --index mpedia --config elastic/index_config.json
```
   * create_index.py script creates an index in elasticsearch
   * `--index` and `--config` arguments specify the name of the elasticsearch index and schema of the target index, respectively.
   * You can verify the index by checking http://127.0.0.1:9200/mpedia

### 7. Create documents
```bash
python3 elastic/create_document.py --index mpedia --csv exported_data/mpedia_chapters.csv --output exported_data/mpedia_chapters.json
```
   * This script creates an `example.json1` file in the elasticsearch prescribed format which in-turn to be indexed later.
   
### 8. Create indexes
```bash
python3 elastic/index_documents.py --data exported_data/mpedia_chapters.json
```
   * This scripts generates the actual indexes and saves it into elasticsearch
   * verify it by checking http://127.0.0.1:9200/mpedia/_search

### 9. Test the engine.
```bash
python3 elastic/elastic.py
```

### 10. Open browser
Go to: http://127.0.0.1:5000