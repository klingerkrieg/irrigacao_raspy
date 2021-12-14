from os import path
import json
from constants import *

CONFIG_JSON = "config.json"

def initialize_json():
    if path.exists(CONFIG_JSON) == False:
        with open(CONFIG_JSON, 'w') as f:
            config = {"last_day": "",
                    "current_time":"",
                    "precipitation_today": "",
                    "next_precipitation": "",
                    "precipitation_limit": "2.0",
                    "valves":[{"irrigation": IRR_WAITING, 
                            "scheduled_time": "10:00:00", 
                            "duration": "00:00:20", 
                            "name": "atras", 
                            "gpio": 1, 
                            "remains": "00:00:00", 
                            "irrigated":"00:00:00"},

                            {"irrigation": IRR_WAITING, 
                            "scheduled_time": "10:00:00", 
                            "duration": "00:00:20", 
                            "name": "frente", 
                            "gpio": 2, 
                            "remains": "00:00:00", 
                            "irrigated":"00:00:00"}]
                    }
            json.dump(config,f)

def read_json():
    with open(CONFIG_JSON, 'r') as f:
        config = json.load(f)
        return config

def write_json(config):
    with open(CONFIG_JSON, 'w') as f:
        json.dump(config,f)