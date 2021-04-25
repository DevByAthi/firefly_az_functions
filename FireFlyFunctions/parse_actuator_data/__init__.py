"""
parse_actuator_data.py

Query for sensor readings at a regular interval (may change trigger). Use sensor readings that detect a wildfire to
estimate where the fire is After parsing sensor data to obtain coordinates of triggered sensors, apply Welzl's
Algorithm to finding the minimum enclosing circle to estimate the wildfire's outer boundary

After running Welzl's Algorithm, return a fixed number of points on the circumference, spaced at regular intervals.
These coordinates will form the flight path of the drone, and they will be sent via the Azure IoT Hub direct method
protocol

Azure Function made by Athreya Murali
Welzl's Algorithm implementation made by Karmela Flynn
Vincenty Direct Method implementation made by Paul Kennedy and Jim Leven

Last Modified: 25 April 2021, 4:09 AM EDT
"""

import logging
import os
from datetime import datetime, timedelta

import azure.functions as func
import geojson
from azure.cosmos import CosmosClient

import numpy as np

from ..shared_code.shared_utils import dict_to_str
from ..shared_code.welzl import welzl, NSphere
from ..shared_code.vincenty import vincentyDirect_kennedy

# Number of desired points on circumference of minimum enclosing circle
NUM_POINTS = 10

# Number of iterations needed for Welzl's Algorithm, multiplied by the number of points
# TODO: Find optimal iteration factor / formula w.r.t. number of input points
ITERATION_FACTOR = 10

# Custom log level used for debug purposes
LEVEL = 25

# TODO: Wrap in a try-except block in a function to avoid spaghetti coding
#  and handle potential connection errors
CLIENT = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database_name = 'sensors'
DATABASE = CLIENT.get_database_client(database_name)
container_name = 'data'
CONTAINER = DATABASE.get_container_client(container_name)

LOGGER = logging.getLogger('log')


def main(mytimer: func.TimerRequest):
    LOGGER.setLevel(LEVEL)

    # Get current time for timestamp-based query filter
    current_time = datetime.now()
    prev_time = current_time - timedelta(hours=2)
    converted_time = datetime.timestamp(prev_time)
    LOGGER.log(LEVEL, "Time: {}".format(converted_time))

    # Query Cosmos DB with timestamp clause
    # NOTE: This may later be done via a stored proc on the Cosmos DB emulator
    # TODO: Consider sensor readings as criteria for query, need significant readings
    query_str = "SELECT * FROM data r WHERE r._ts >= @time"

    query_results = list(CONTAINER.query_items(query=query_str, parameters=[{"name": "@time", "value": converted_time}],
                                               enable_cross_partition_query=True))
    LOGGER.log(LEVEL, "LENGTH: {}".format(len(query_results)))

    # Create aggregation set for coordinates retrieved from query
    # A set prevents duplicate coordinates from being stored, which would impede
    # the performance of Welzl's Algorithm
    coordinates = set()
    for doc in query_results:
        # TODO: Check that `doc` has the below keys before accessing, may cause KeyError otherwise
        point_list = doc['geometry']['coordinates']
        point = (point_list[0], point_list[1])
        coordinates.add(point)

    # Check if there are any coordinates from recent sensor readings of significance
    if len(coordinates) == 0:
        LOGGER.log(LEVEL, "No coordinates retrieved")
        return
    LOGGER.log(LEVEL, "Sensor coordinates retrieved: {}".format(coordinates))

    # Apply Welzl's Algo to parsed coordinates
    coord_list = list(coordinates)
    max_iterations = len(coord_list) * ITERATION_FACTOR
    nsphere: NSphere = welzl(points=coord_list, maxiterations=max_iterations)

    # Log coordinates and radius of minimum enclosing circle
    LOGGER.log(LEVEL, "Center: {}, Radius: {}".format(nsphere.center, nsphere.sqradius))

    # Send out points along circumference of minimum enclosing circle
    for bearing in range(0, 360, 360 // NUM_POINTS):
        lat, lon, _ = vincentyDirect_kennedy(nsphere.center[0], nsphere.center[1], 1000 * (nsphere.sqradius ** 0.5),
                                             bearing)
        LOGGER.log(LEVEL, "Coordinates on Circumference: ({}, {})".format(lat, lon))

    # TODO: Send out coordinates on circumference to IoT Hub drones via direct method, will need IotHubRegistry
