import logging
import collections
from flask import json

class DbParser():
    def __init__(self) -> None:
        pass
    

    def event2OrderedDict(self, row):
        
        # Convert query to objects of key-value pairs
        d = collections.OrderedDict()
        d["id"] = row[0]
        d["created_at"] = row[1]
        d["date"] = row[2]
        d["starting_point_long"] = row[3]
        d["starting_point_lat"] = row[4]
        d["difficulty_level"] = row[5]
        d["avg_pace_min"] = row[6]
        d["avg_pace_sec"] = row[7]
        d["avg_duration"] = row[8]
        d["avg_length"] = row[9]
        d["admin_id"] = row[10]
        d["current_participants"]  = row[11]
        d["max_participants"] = row[12]
        
        return d

    def event2Json(self, event):
        events_list = []
        for row in event:
            events_list.append(self.event2OrderedDict(row))

        j = json.dumps(events_list[0])
        return j

    def events2Json(self, events):

        # Convert query to objects of key-value pairs
        events_list = []
        for row in events:
            events_list.append(self.event2OrderedDict(row))
            
        j = json.dumps(events_list)
        logging.info(j)

        return j
    
    def eventId2Json(self, eventId):

        d = collections.OrderedDict()
        d["id"] = eventId
        j = json.dumps(d)
        logging.info(j)

        return j

    # BOOKINGS

    def booking2OrderedDict(self, row):
        
        # Convert query to objects of key-value pairs
        d = collections.OrderedDict()
        d["id"] = row[0]
        d["created_at"] = row[1]
        d["user_id"] = row[2]
        d["event_id"] = row[3]
        
        return d

    def bookings2Json(self, bookings):
        bookings_list = []
        for row in bookings:
            bookings_list.append(self.booking2OrderedDict(row))

        j = json.dumps(bookings_list)
        logging.info(j)

        return j

    def bookingId2Json(self, bookingId):

        d = collections.OrderedDict()
        d["id"] = bookingId
        j = json.dumps(d)
        logging.info(j)

        return j

    # USERS

    def user2OrderedDict(self, row):
        
        # Convert query to objects of key-value pairs
        d = collections.OrderedDict()
        d["id"] = row[0]
        d["name"] = row[1]
        d["surname"] = row[2]
        d["height"] = row[3]
        d["age"] = row[4]
        d["fitness_level"] = row[5]
        d["city"] = row[6]
        
        return d

    def user2Json(self, user):

        users_list = []
        for row in user:
            users_list.append(self.user2OrderedDict(row))

        j = json.dumps(users_list[0])
        
        logging.info(j)
        return j   