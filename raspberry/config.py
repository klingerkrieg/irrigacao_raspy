from os import path, read
import json
from constants import *

CONFIG_JSON = "config.json"

def initialize_json(force=False):
    if path.exists(CONFIG_JSON) == False or force:
        with open(CONFIG_JSON, 'w') as f:
            config = {"last_day": "",
                    "current_time":"",
                    "precipitation_today": "",
                    "next_precipitation": "",
                    "precipitation_limit": "2.0",
                    "valves":[{"irrigation": IRR_WAITING, 
                            "scheduled_time": "18:00:00", 
                            "duration": "00:08:00", 
                            "name": "atras", 
                            "gpio": 4, 
                            "remains": "00:00:00", 
                            "irrigated":"00:00:00"},

                            {"irrigation": IRR_WAITING, 
                            "scheduled_time": "18:10:00", 
                            "duration": "00:10:00", 
                            "name": "frente", 
                            "gpio": 26, 
                            "remains": "00:00:00", 
                            "irrigated":"00:00:00"}]
                    }
            json.dump(config,f)

def read_json():
    with open(CONFIG_JSON, 'r') as f:
        try:
            config = json.load(f)
            return config
        except:
            txt = f.read()
            if (txt == ""):
                initialize_json(True)
                return read_json()
            print(CONFIG_JSON,":",)
            raise Exception

def write_json(config):
    with open(CONFIG_JSON, 'w') as f:
        json.dump(config,f)