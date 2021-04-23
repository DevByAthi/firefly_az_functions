import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient

CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])


def main(documents: func.DocumentList) -> str:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])
        logging.info("Documents List length: {}".format(len(documents)))
        if 'geometry' not in documents[0]:
            return "FAILED TO RETRIEVE CORRECT DOCUMENT"
        return str(documents[0]['geometry']).replace("'", '"')
