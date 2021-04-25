import logging
import os
from datetime import datetime, timedelta

import azure.functions as func
from azure.cosmos import CosmosClient

CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database_name = 'sensors'
DATABASE = CLIENT.get_database_client(database_name)
container_name = 'data'
CONTAINER = DATABASE.get_container_client(container_name)


def main(mytimer: func.TimerRequest):
    current_time = datetime.now()
    prev_time = current_time - timedelta(minutes=20)
    converted_time = datetime.timestamp(prev_time)
    logging.info("Time: {}".format(converted_time))

    # TODO: Create aggregation list for coordinates retrieved from query

    # TODO: Query Cosmos DB with timestamp clause, limit clause, and (if possible) a distance clause
    #   NOTE: This may later be done via a stored proc on the Cosmos DB emulator
    query_str = "SELECT * FROM data r WHERE r._ts >= @time"

    # read_results = list(CONTAINER.read_all_items(max_item_count=20))
    query_results = list(CONTAINER.query_items(query=query_str, parameters=[{"name": "@time", "value": converted_time}],
                                               enable_cross_partition_query=True))
    print("LENGTH: {}".format(len(query_results)))
    for doc in query_results:
        print("{}: {}".format(doc['id'], doc['geometry']['coordinates']))
    # TODO: Apply Welzl's Algo to parsed coordinates

    # TODO: Obtain coordinates and radius of minimum enclosing circle

    # TODO: Send out points along circumference
