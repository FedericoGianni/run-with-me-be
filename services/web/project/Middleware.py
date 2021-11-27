import logging
import datetime 

from project.dbmysql.DbController import DbController
import ApiHelpers as utils

class Middleware():
    def __init__(self) -> None:
        self.dbController = DbController()
        pass

    def register(self, message):
        pass

    def getEvents(self, long, lat, max_dist_km):
        logging.info("long: " + str(long) + " lat: " + str(lat) + " max_dist_km: " + str(max_dist_km))
        events = self.dbController.getEvents(long, lat, max_dist_km)
        return events

    def getEventById(self, id):
        logging.info("id: " + str(id))
        event = self.dbController.getEventById(id)
        return event

    def addEvent(self, date, name, starting_point_long, starting_point_lat, avg_duration, avg_length, avg_pace_min, avg_pace_sec, admin_id, max_participants):
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

        date = datetime.datetime.fromtimestamp(date)

        if(avg_pace_min == None or avg_pace_sec == None):
            avg_pace = utils.calculateAvgPace(avg_length, avg_duration)

        difficulty_level = utils.calculateDifficultyLevel(avg_length, avg_duration)

        current_participants = 1

        self.dbController.addEvent(created_at, date, name, starting_point_long, starting_point_lat, difficulty_level, avg_pace_min, avg_pace_sec, avg_duration, avg_length, admin_id, current_participants, max_participants)


        return 