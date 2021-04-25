import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient

CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])


# TODO: Use Timer trigger instead of IoT Hub trigger
def main(documents: func.DocumentList):

    # TODO: Create aggregation list for coordinates retrieved from query

    # TODO: Query Cosmos DB with timestamp clause, limit clause, and (if possible) a distance clause
    #   NOTE: This may later be done via a stored proc on the Cosmos DB emulator

    # TODO: Apply Welzl's Algo to parsed coordinates

    # TODO: Obtain coordinates and radius of minimum enclosing circle

    # TODO: Send out points along circumference
    if documents:
        logging.info('Document id: %s', documents[0]['id'])
        logging.info("Documents List length: {}".format(len(documents)))
        for i in range(len(documents)):
            doc = documents[i]
            print("Document #{}: {}".format(i, doc['id']))