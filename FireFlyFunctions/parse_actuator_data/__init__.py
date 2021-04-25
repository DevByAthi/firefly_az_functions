import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient

CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])


def main(documents: func.DocumentList):
    if documents:
        logging.info('Document id: %s', documents[0]['id'])
        logging.info("Documents List length: {}".format(len(documents)))
        for i in range(len(documents)):
            doc = documents[i]
            print("Document #{}: {}".format(i, doc['id']))