from os import path
import datetime
import json

HISTORY_JSON = "history.json"


def add_history(msg, config, valve={"remains":"","scheduled_time":"", "irrigated":""}):
    if path.exists(HISTORY_JSON) == False:
        with open(HISTORY_JSON, 'w') as f:
            f.write("{}")
            f.close()

    with open(HISTORY_JSON, 'r') as f:
        hist = json.load(f)
        f.close()

    with open(HISTORY_JSON, 'w') as f:
        id = len(hist)
        hour = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        hist[id] = {"msg":msg,
                    "hour":hour,
                    "precipitation_today": config["precipitation_today"], 
                    "next_precipitation": config["next_precipitation"],
                    "remains":valve["remains"],
                    "irrigated":valve["irrigated"],
                    "scheduled_time":valve["scheduled_time"]}
        json.dump(hist,f)
        f.close()
