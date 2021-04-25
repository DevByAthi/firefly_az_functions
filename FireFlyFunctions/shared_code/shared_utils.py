import geojson




def dict_to_str(d: dict) -> str:
    return str(d).replace("'", '"')


def is_device_sensor(payload: geojson.Feature) -> bool:
    """
    Assumes that payload is a geojson.Feature
    :param payload:
    :return:
    """
    if 'device_type' not in payload['properties']:
        return False
    if payload['properties']['device_type'] == 'sensor':
        return True
    elif payload['properties']['device_type'] == 'actuator':
        return False
    raise KeyError("Device type must either be a 'sensor' or an 'actuator'!")


def meets_device_format(d):
    return isinstance(d, geojson.Feature) and 'device_type' in d['properties']


def get_always_fire(payload: dict) -> bool:
    return True


def get_mock_decision(payload: dict) -> bool:
    """
    A fake function for deciding on whether a wildfire is detected at a given sensor, using sensor's data payload and
    preset threshold parameters. In reality, the linear combination of values would be decided by hyper-parameter tuning
    via an ML algorithm.
    :param payload:
    :return:
    """
    THRESHOLD = 0.5
    has_valid_data = 'temperature' in payload and 'humidity' in payload and \
                     'carbon_monoxide' in payload and 'pm2_5' in payload
    if has_valid_data:
        return 0.2 * payload['temperature'] + 0.05 * payload['humidity'] + \
               0.6 * payload['carbon_monoxide'] + 0.15 * payload['pm2_5'] > THRESHOLD
    return False
