"""
Miscellaneous Utility Functions

by Athreya Murali

Last Modified: 3 May 2021, 8:55 PM EDT

"""

import geojson

def dict_to_str(d: dict) -> str:
    """
    Converts dictionary to a JSON-friendly string
    :param d: input dictionary
    :return: JSON-formatted string
    """
    return str(d).replace("'", '"')


def is_device_sensor(payload: geojson.Feature) -> bool:
    """
    Checks if given GeoJSON payload has a 'device_type' property, and checks that it is either a "sensor" or "actuator"
    :param payload: GeoJSON payload
    :return: boolean determining if payload is from a sensor or actuator
    :exception: KeyError if 'device_type' is neither "sensor" nor "actuator"
    """
    if 'device_type' not in payload['properties']:
        return False
    if payload['properties']['device_type'] == 'sensor':
        return True
    elif payload['properties']['device_type'] == 'actuator':
        return False
    raise KeyError("Device type must either be a 'sensor' or an 'actuator'!")


def meets_device_format(d):
    """
    Returns boolean determining if given dictionary `d` or GeoJSON payload has a 'device_type' property
    """
    return isinstance(d, geojson.Feature) and 'device_type' in d['properties']

