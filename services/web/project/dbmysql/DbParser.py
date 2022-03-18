import logging
import collections
import datetime
from flask import json

class DbParser():
    def __init__(self) -> None:
        pass
    
    
    def dateStringToTimeStamp(self, date):
        return date.timestamp()

    def errorMsg2Json(self, msg):

        d = collections.OrderedDict()
        d["msg"] = msg
        j = json.dumps(d)
        logging.info(j)

        return j

    def event2OrderedDict(self, row):
        
        # Convert query to objects of key-value pairs
        d = collections.OrderedDict()
        d["id"] = row[0]
        d["created_at"] = self.dateStringToTimeStamp(row[1])
        d["name"] = row[2]
        d["date"] = self.dateStringToTimeStamp(row[3])
        d["starting_point_long"] = row[4]
        d["starting_point_lat"] = row[5]
        d["difficulty_level"] = row[6]
        d["avg_pace_min"] = row[7]
        d["avg_pace_sec"] = row[8]
        d["avg_duration"] = row[9]
        d["avg_length"] = row[10]
        d["admin_id"] = row[11]
        d["current_participants"]  = row[12]
        d["max_participants"] = row[13]
        
        return d

    def event2Json(self, event):
        events_list = []
        for row in event:
            events_list.append(self.event2OrderedDict(row))

        if(not events_list):
            j = None
        else: 
            j = json.dumps(events_list[0])
        return j

    def events2OrderedDict(self, events):
        # Convert query to objects of key-value pairs
        events_list = []
        for row in events:
            events_list.append(self.event2OrderedDict(row))

        return events_list

    def events2Json(self, events):

        # Convert query to objects of key-value pairs
        events_list = []
        for row in events:
            events_list.append(self.event2OrderedDict(row))
            
        j = json.dumps(events_list)
        logging.info(j)

        return j

    def eventsDict2Json(self, events):
        
        j = json.dumps(events)
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
        d["created_at"] = self.dateStringToTimeStamp(row[1])
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

    def bookings2OrderedDict(self, bookings):
        bookings_list = []
        for row in bookings:
            bookings_list.append(self.booking2OrderedDict(row))

        return bookings_list

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
        d["username"] = row[1] 
        #don't need to return password for user infos
        #d["password"] = row[2]
        d["email"] = row[3]
        d["name"] = row[4]
        d["surname"] = row[5]
        d["created_at"] = self.dateStringToTimeStamp(row[6])
        d["height"] = row[7]
        d["age"] = row[8]
        d["sex"] = row[9]
        d["fitness_level"] = row[10]
        d["city"] = row[11]
        
        return d

    def user2OrderedDictWithPass(self, row):
        
        # Convert query to objects of key-value pairs
        d = collections.OrderedDict()
        d["id"] = row[0]
        d["username"] = row[1] 
        d["password"] = row[2]
        d["email"] = row[3]
        d["name"] = row[4]
        d["surname"] = row[5]
        d["created_at"] = self.dateStringToTimeStamp(row[6])
        d["height"] = row[7]
        d["age"] = row[8]
        d["sex"] = row[9]
        d["fitness_level"] = row[10]
        d["city"] = row[11]
        
        return d

    def user2Json(self, user):

        users_list = []
        for row in user:
            users_list.append(self.user2OrderedDict(row))

        j = json.dumps(users_list[0])
        
        logging.info(j)
        return j   

    def userId2Json(self, userId):

        d = collections.OrderedDict()
        d["id"] = userId
        j = json.dumps(d)
        logging.info(j)

        return j