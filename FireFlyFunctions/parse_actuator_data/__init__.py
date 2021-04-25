import logging
import os
from datetime import datetime, timedelta

import azure.functions as func
import geojson
import pygeodesy as pyg
from azure.cosmos import CosmosClient

import numpy as np

from ..shared_code.shared_utils import dict_to_str
from ..shared_code.welzl import welzl, NSphere

LEVEL = 25

CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database_name = 'sensors'
DATABASE = CLIENT.get_database_client(database_name)
container_name = 'data'
CONTAINER = DATABASE.get_container_client(container_name)

LOGGER = logging.getLogger('log')


def main(mytimer: func.TimerRequest):
    LOGGER.setLevel(LEVEL)
    current_time = datetime.now()
    prev_time = current_time - timedelta(hours=2)
    converted_time = datetime.timestamp(prev_time)
    LOGGER.log(LEVEL, "Time: {}".format(converted_time))

    # TODO: Create aggregation list for coordinates retrieved from query

    # TODO: Query Cosmos DB with timestamp clause, limit clause, and (if possible) a distance clause
    #   NOTE: This may later be done via a stored proc on the Cosmos DB emulator
    query_str = "SELECT * FROM data r WHERE r._ts >= @time"

    # read_results = list(CONTAINER.read_all_items(max_item_count=20))
    query_results = list(CONTAINER.query_items(query=query_str, parameters=[{"name": "@time", "value": converted_time}],
                                               enable_cross_partition_query=True))
    LOGGER.log(LEVEL, "LENGTH: {}".format(len(query_results)))

    coordinates = set()
    for doc in query_results:
        point_list = doc['geometry']['coordinates']
        point = (point_list[0], point_list[1])
        point_str = "{},{}".format(point_list[0], point_list[1])
        # LOGGER.log(LEVEL, "{}: {}".format(doc['id'], point_list))

        coordinates.add(point)

    LOGGER.log(LEVEL, coordinates)

    # TODO: Apply Welzl's Algo to parsed coordinates
    coord_list = list(coordinates)
    max_iterations = len(coord_list) * 10
    nsphere: NSphere = welzl(points=coord_list, maxiterations=max_iterations)

    LOGGER.log(LEVEL, "Center: {}, Radius: {}".format(nsphere.center, nsphere.sqradius))

    # TODO: Obtain coordinates and radius of minimum enclosing circle

    # TODO: Send out points along circumference
