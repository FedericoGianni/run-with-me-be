import logging
import collections
from flask import json

class DbParser():
    def __init__(self) -> None:
        pass

    def event2Json(self, events):

        # Convert query to objects of key-value pairs
        events_list = []
        for row in events:
            d = collections.OrderedDict()
            d["id"] = row[0]
            d["created_at"] = row[1]
            d["date"] = row[2]
            d["starting_point_long"] = row[3]
            d["starting_point_lat"] = row[4]
            d["difficulty_level"] = row[5]
            d["avg_pace"] = row[6]
            d["avg_duration"] = row[7]
            d["avg_length"] = row[8]
            d["admin_id"] = row[9]
            d["current_participants"]  = row[10]
            d["max_participants"] = row[11]
            events_list.append(d)
            
        j = json.dumps(events_list)
        logging.info(j)

        return j
        