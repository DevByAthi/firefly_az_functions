import json

class SensorDataPoint:
    def __init__(self, temperature, pm2, pm10, co):
        self.temperature = temperature
        self.pm2 = pm2
        self.pm10 = pm10
        self.carbon_monoxide = co

    @staticmethod
    def convert_from_json(json_str):
        pass