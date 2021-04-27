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
from azure.iot.device import IoTHubDeviceClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from msrest.exceptions import HttpOperationError

from ..shared_code.shared_utils import dict_to_str
from ..shared_code.welzl import welzl, NSphere
from ..shared_code.vincenty import vincentyDirect_kennedy

# Number of desired points on circumference of minimum enclosing circle
NUM_POINTS = 10

# Number of iterations needed for Welzl's Algorithm, multiplied by the number of points
ITERATION_FACTOR = 10

# Custom log level used for debug purposes
LEVEL = 25

CLIENT = None
DATABASE = None
CONTAINER = None

IOT_REGISTRY_MANAGER = IoTHubRegistryManager("HostName=iotmurali.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=8pb/ntX+rPMwZs6bgDf8u1XI7aFncHfcX56/ZUsDEbk=")
DEVICE_ID = "MyPythonDevice"
METHOD_NAME = "DetermineFlightPath"

LOGGER = logging.getLogger('log')


def init_connections():
    global CLIENT
    global DATABASE
    global CONTAINER

    global IOT_REGISTRY_MANAGER

    CLIENT = CosmosClient.from_connection_string(os.getenv('AzureCosmosDBConnectionString'))
    database_name = 'sensors'
    DATABASE = CLIENT.get_database_client(database_name)
    container_name = 'data'
    CONTAINER = DATABASE.get_container_client(container_name)


def main(mytimer: func.TimerRequest):
    LOGGER.setLevel(LEVEL)
    timestamps = []
    if not (CONTAINER and DATABASE and CLIENT):
        init_connections()

    # Get current time for timestamp-based query filter
    current_time = datetime.now()
    prev_time = current_time - timedelta(hours=2)
    converted_time = datetime.timestamp(prev_time)
    LOGGER.log(LEVEL, "Time: {}".format(converted_time))

    timestamps.append(("Initialization", current_time))

    # Query Cosmos DB with timestamp clause
    # NOTE: This may later be done via a stored proc on the Cosmos DB emulator
    # TODO: Consider sensor readings as criteria for query, need significant readings
    query_str = "SELECT * FROM data r WHERE r._ts >= @time AND r.properties.carbon_monoxide.val > 12 AND r.properties.pm2_5.val > 5"

    query_results = list(CONTAINER.query_items(query=query_str, parameters=[{"name": "@time", "value": converted_time}],
                                               enable_cross_partition_query=True))
    LOGGER.log(LEVEL, "LENGTH: {}".format(len(query_results)))

    timestamps.append(("Finished Query", datetime.now()))

    # Create aggregation set for coordinates retrieved from query
    # A set prevents duplicate coordinates from being stored, which would impede
    # the performance of Welzl's Algorithm
    coordinates = set()
    for doc in query_results:
        # TODO: Check that `doc` has the below keys before accessing, may cause KeyError otherwise
        point_list = doc['geometry']['coordinates']
        point = (point_list[0], point_list[1])
        coordinates.add(point)
    timestamps.append(("Finished Query", datetime.now()))

    # Check if there are any coordinates from recent sensor readings of significance
    if len(coordinates) < 3:
        LOGGER.log(LEVEL, "Not enough coordinates retrieved to apply Welzl's Algorithm")
        return
    LOGGER.log(LEVEL, "Sensor coordinates retrieved: {}".format(coordinates))

    # Apply Welzl's Algo to parsed coordinates
    coord_list = list(coordinates)
    max_iterations = len(coord_list) * ITERATION_FACTOR
    nsphere: NSphere = welzl(points=coord_list, maxiterations=max_iterations)
    timestamps.append(("Finished Welzl's Algorithm", datetime.now()))

    # Log coordinates and radius of minimum enclosing circle
    LOGGER.log(LEVEL, "Center: {}, Radius: {}".format(nsphere.center, nsphere.sqradius))

    # Send out points along circumference of minimum enclosing circle
    mission_coords = []
    for bearing in range(0, 360, 360 // NUM_POINTS):
        lat, lon, _ = vincentyDirect_kennedy(nsphere.center[0], nsphere.center[1], 1000 * (nsphere.sqradius ** 0.5),
                                             bearing)
        mission_coords.append((lat, lon))
        LOGGER.log(LEVEL, "Coordinates on Circumference: ({}, {})".format(lat, lon))
    timestamps.append(("Finished Vincenty's Direct Method", datetime.now()))

    try:
        mission_geojson = geojson.MultiPoint(mission_coords)
        if mission_geojson.is_valid:
            # Send out coordinates on circumference to IoT Hub drones via direct method via IoTHubRegistryManager
            device_method = CloudToDeviceMethod(method_name=METHOD_NAME, payload=mission_geojson)
            response = IOT_REGISTRY_MANAGER.invoke_device_method(DEVICE_ID, device_method)
            print("Response Payload: {}".format(response.payload))
    except ValueError:
        return
    except HttpOperationError as e:
        print("No available idle drones for mission!")
        timestamps.append(("Finished Sending Payload to Drone", datetime.now()))

    for i in range(1, len(timestamps)):
        curr, prev = timestamps[i], timestamps[i-1]
        print("\033[92m {}: difference is {} from previous stage {} \033[00m".format(curr[0], curr[1] - prev[1], prev[0]))
