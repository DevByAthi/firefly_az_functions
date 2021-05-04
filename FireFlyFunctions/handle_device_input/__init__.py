"""
handle_device_input
a.k.a. Azure Function 2

===================

This function triggers when the associated IoT Hub receives new device data. When triggered, the function will obtain the data record and do the following:
1. Parse it into a GeoJSON-formatted object
2. Check that GeoJSON record has a 'device_type' property
3. If parsed record is invalid and does not meet necessary criteria, SKIP and wait for next record
4. If 'device_type' is a sensor, then insert record into the 'sensors' table in the associated Cosmos DB database
5. Otherwise, 'device_type' must be actuator, so insert record into the 'actuators' table in the associated Cosmos DB database

Azure Function made by Athreya Murali

Last Modified: 3 May 2021, 8:46 PM EDT
"""


import json.decoder
import os
from typing import List
import logging
import geojson

import azure.functions as func

from ..shared_code.shared_utils import meets_device_format, is_device_sensor


def main(events: List[func.EventHubEvent], actmsg: func.Out[func.Document], sensmsg: func.Out[func.Document]):
    for event in events:
        decoded_message = event.get_body().decode('utf-8')

        # dictionary obtained from message
        decoded_dict = None

        # logging.info("TEST 1")

        try:
            decoded_dict = geojson.loads(decoded_message)
        except json.decoder.JSONDecodeError:
            continue
        # logging.info("TEST 2: Successfully converted to dict without error")

        # Ensure that GeoJSON format is met, with requirement that event be from an "actuator", i.e. drone
        if decoded_dict is None or not meets_device_format(decoded_dict):
            continue
        # logging.info("TEST 3: Meets defined GeoJSON format")

        try:
            is_sensor = is_device_sensor(decoded_dict)
        except KeyError:
            # logging.info("INVALID DEVICE TYPE!")
            continue
        # logging.info("TEST 4: Is a valid device reading")

        # logging.info('Python EventHub trigger processed an event: %s', decoded_message)

        # Send data to correct database depending on device type
        if is_sensor:
            sensmsg.set(func.Document.from_dict(decoded_dict))
        else:
            actmsg.set(func.Document.from_dict(decoded_dict))
        # logging.info("TEST 5: Successfully sent")
