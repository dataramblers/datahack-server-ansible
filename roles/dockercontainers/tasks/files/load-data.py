#!/usr/bin/env python2.7

from elasticsearch import Elasticsearch
import json
import os
import time
import argparse
from tqdm import tqdm


class Importer:

    """
    A simple class to build a elastic search index for the sah data
    """

    def __init__(self, es_host="localhost", es_port=9200):
        self.es = Elasticsearch(hosts=[{'host': es_host, 'port': es_port}],)

    def batch(self, index, doc_type, body, counter=0):
        """
        Load data into the index
        :param index: Name of the index
        :param doc_type: Name of the doc_type
        :param body: Data to index
        :param counter: internal counter for failure retry
        :return:
        """
        try:
            self.es.bulk(index=index, doc_type=doc_type, body=body)
        except Exception:
            print("Error: Failed to import a part of the data set. "
                  "Try again to import segment for the {} time".format(counter + 1))
            time.sleep(10)
            counter += 1
            self.batch(index, doc_type, body, counter)

    def bootstrap(self, index, mapping_file="mapping.json"):
        """
        Bootstrap es index. Delete existing index and create a new one with mapping
        :param index: Name of the index
        :param mapping_file: The definition for the mapping
        :return:
        """
        mapping = {}
        if os.path.isfile(mapping_file):
            mapping = open(mapping_file).read()

        if self.es.indices.exists(index):
            self.es.indices.delete(index)
        self.es.indices.create(index, mapping)

    def load(self, json_file, index="sah", doc_type="doc", bulk_size=50000):
        """
        Load data for a file into Es-Index
        :param json_file: The json file with the data to index
        :param index: Name of the index
        :param doc_type: Name of the doc_type
        :param bulk_size: The bulksize for committing the data into the es index
        :return:
        """
        cache = list()
        counter = 0
        fp = open(json_file, 'r')
        json_objects = json.loads(fp.read())

        with tqdm(total=len(json_objects)) as pbar:
            for json_object in json_objects:
                pbar.update()
                # todo: more generic with composition or configuration
                doc_id = json_object['Signatur']
                # convert isbn numbers
                header = '{ "index" : { "_index" : "' + index + '", "_type" : "' + doc_type + \
                         '", "_id" : "' + str(hash(doc_id)) + '" } }'
                cache.append(header)
                cache.append(json.dumps(json_object))
                counter += 1
                if counter >= bulk_size:
                    self.batch(index, doc_type, "\n".join(cache))
                    cache = []
                    counter = 0
            if counter > 0:
                self.batch(index, doc_type, "\n".join(cache))

        pbar.close()


parser = argparse.ArgumentParser(description='Load json data from sah into an elastic search index.')
parser.add_argument('data', type=str, help='Path to the json file')
parser.add_argument('--es-host', type=str, help='Elastic search host', default="localhost")
parser.add_argument('--es-port', type=int, help='Elastic search port', default=9200)
parser.add_argument('--es-index',  type=str, help='Elastic search index', default="sah")
parser.add_argument('--es-doc-type',  type=str, help='Elastic search doctype', default="doc")
parser.add_argument('--es-flush',  type=bool, help='Flush and create the elastic search index', default=False)
parser.add_argument('--mapping-file',  type=str, help='Mapping file for the index', default="mapping.json")
parser.add_argument('--bulk-size', type=int, help='Bulk size for the import', default=50000)
args = parser.parse_args()
importer = Importer(args.es_host, args.es_port)
# flush data and create index
if args.es_flush:
    importer.bootstrap(args.es_index, args.mapping_file)
# import data
importer.load(args.data, args.es_index, args.es_doc_type, args.bulk_size)
