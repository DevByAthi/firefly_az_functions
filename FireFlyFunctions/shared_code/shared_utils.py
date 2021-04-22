import geojson


def meets_device_format(d, is_sensor=True):
    expected_device_type = 'sensor' if is_sensor else 'actuator'
    return isinstance(d, geojson.Feature) \
           and 'device_type' in d['properties'] \
           and d['properties']['device_type'] == expected_device_type


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
