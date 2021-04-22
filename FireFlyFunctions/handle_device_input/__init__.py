import json.decoder
import os
from typing import List
import logging
import geojson

import azure.functions as func

from ..shared_code.shared_utils import meets_device_format, is_device_sensor


def main(events: List[func.EventHubEvent], msg: func.Out[func.Document]):
    for event in events:
        decoded_message = event.get_body().decode('utf-8')

        # dictionary obtained from message
        decoded_dict = None

        logging.info("TEST 1")

        try:
            decoded_dict = geojson.loads(decoded_message)
        except json.decoder.JSONDecodeError:
            continue
        logging.info("TEST 2: Successfully converted to dict without error")

        # Ensure that GeoJSON format is met, with requirement that event be from an "actuator", i.e. drone
        if decoded_dict is None or not meets_device_format(decoded_dict):
            continue
        logging.info("TEST 3: Meets defined GeoJSON format")

        try:
            device_type = is_device_sensor(decoded_dict)
        except KeyError:
            continue
        logging.info("TEST 4: Is a valid device reading")

        logging.info('Python EventHub trigger processed an event: %s', decoded_message)

        # TODO: Send data to correct database depending on device type
        msg.set(func.Document.from_dict(decoded_dict))
        logging.info("TEST 5: Successfully sent")
