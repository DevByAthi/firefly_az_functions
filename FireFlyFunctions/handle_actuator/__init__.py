import json.decoder
import os
from typing import List
import logging
import geojson

import azure.functions as func

from ..shared_code.shared_utils import meets_device_format


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
        if decoded_dict is None or not meets_device_format(decoded_dict, is_sensor=False):
            continue

        logging.info("TEST 3: Meets defined GeoJSON format")

        logging.info('Python EventHub trigger processed an event: %s', decoded_message)
        msg.set(func.Document.from_dict(decoded_dict))
        logging.info("TEST 4: Successfully sent")
