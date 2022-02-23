import logging
import datetime 
import bcrypt

from project.dbmysql.DbController import DbController
import ApiHelpers as utils

class Middleware():
    def __init__(self) -> None:
        self.dbController = DbController()
        pass

    def register(self, message):
        pass

# EVENTS 

    def getEvents(self, long, lat, max_dist_km):
        logging.info("long: " + str(long) + " lat: " + str(lat) + " max_dist_km: " + str(max_dist_km))
        events = self.dbController.getEvents(long, lat, max_dist_km)
        return events

    def getEventById(self, id):
        logging.info("id: " + str(id))
        event = self.dbController.getEventById(id)
        return event

    def getEventsByAdminId(self, admin_id):
        logging.info("id: " + str(admin_id))
        return self.dbController.getEventsByAdminId(admin_id)

    def getEventsByUserId(self, user_id):
        logging.info("id: " + str(user_id))
        return self.dbController.getEventsByUserId(user_id)

    def addEvent(self, event):
        #   id int [pk, increment] // auto-increment
        #   created_at datetime MIDDLEWARE
        #   name varchar
        #   date datetime MIDDLEWARE -> CONVERT FROM TIMESTAMP
        #   starting_point_long float
        #   starting_point_lat float
        #   difficulty_level float -> MIDDLEWARE CALCULATE DINAMICALLY
        #   avg_pace_min int
        #   avg_pace_sec int
        #   avg_duration int
        #   avg_length int
        #   admin_id int [ref: > users.id]
        #   current_participants int -> MIDDLEWARE, set to 1
        #   max_participants int

        created_at = datetime.datetime.now()

        date = datetime.datetime.fromtimestamp(event['date'])

        if(event['avg_pace_min'] == None or event['avg_pace_sec'] == None):
            avg_pace = utils.calculateAvgPace(event['avg_length'], event['avg_duration'])

        difficulty_level = utils.calculateDifficultyLevel(event['avg_length'], event['avg_duration'])

        current_participants = 1

        newEvent = {
            "created_at" : created_at,
            "date": date,
            "name": event['name'],
            "starting_point_long" : event['starting_point_long'],
            "starting_point_lat": event['starting_point_lat'],
            "difficulty_level" : difficulty_level,
            "avg_pace_min" : event['avg_pace_min'],
            "avg_pace_sec" : event['avg_pace_sec'],
            "avg_duration" : event['avg_duration'],
            "avg_length" : event['avg_length'],
            "admin_id" : event['admin_id'],
            "current_participants" : current_participants,
            "max_participants" : event['max_participants'],
        }   

        return self.dbController.addEvent(newEvent)

    def deleteEvent(self, event_id):
        return self.dbController.deleteEvent(event_id)

    def updateEvent(self, event_id, updatedEvent):
        
        #removing null parameters 
        updatedEvent = {k: v for k, v in updatedEvent.items() if v}
        if(updatedEvent['date'] != None):
            updatedEvent['date'] = datetime.datetime.fromtimestamp(updatedEvent['date'])

        return self.dbController.updateEvent(event_id, updatedEvent)

# BOOKINGS

    def getBookingsByEventId(self, event_id):
        return self.dbController.getBookingsByEventId(event_id) 

    def getBookingsByUserId(self, user_id):
        return self.dbController.getBookingsByUserId(user_id) 

    def addBooking(self, user_id, event_id):
        booking = {
            "created_at": datetime.datetime.now(),
            "user_id": user_id,
            "event_id": event_id,
        }

        return self.dbController.addBooking(booking)

    def delBooking(self, user_id, event_id):
        return self.dbController.delBooking(user_id, event_id)

    
# USERS

    def getUserInfo(self, user_id):
        return self.dbController.getUserInfo(user_id)

    def addUser(self, user):

        newUser = {
            "name": user['name'],
            "surname": user['surname'],
            "created_at" : datetime.datetime.now(),
            "height": user['height'],
            "age": user['age'],
            "fitness_level": user['fitness_level'],
            "city": user['city'],
        }

        return self.dbController.addUser(newUser)

    def updateUser(self, user_id, updatedUser):
        #removing null parameters 
        updatedUser = {k: v for k, v in updatedUser.items() if v}
        return self.dbController.updateUser(user_id, updatedUser)

    def delUser(self, user_id):
        return self.dbController.delUser(user_id
        )

# AUTH

    def register(self, username, password):
        # TODO aggiungere libreria per hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logging.info("generating hash from password...")
        return self.dbController.register(username, password)

    def login(self, username, password):
        # TODO aggiungere libreria per hash password
        return self.dbController.login(username, password)
