import geojson


def meets_device_format(d, is_sensor=True):
    expected_device_type = 'sensor' if is_sensor else 'actuator'
    return isinstance(d, geojson.Feature) \
           and 'properties' in d \
           and 'device_type' in d['properties'] \
           and d['properties']['device_type'] == expected_device_type
