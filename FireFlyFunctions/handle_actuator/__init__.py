import json.decoder
from typing import List
import geojson

import azure.functions as func

from ..shared_code.shared_utils import meets_device_format


def main(events: List[func.EventHubEvent], out: func.Out[func.Document]):
    for event in events:
        decoded_message = event.get_body().decode('utf-8')
        # logging.info('Python EventHub trigger processed an event: %s',
        #                 event.get_body().decode('utf-8'))

        # dictionary obtained from message
        decoded_dict = None
        try:
            decoded_dict = geojson.loads(decoded_message)
        except json.decoder.JSONDecodeError as err:
            continue

        # Ensure that GeoJSON format is met, with requirement that event be from an "actuator", i.e. drone
        if not meets_device_format(decoded_dict, is_sensor=False):
            continue

