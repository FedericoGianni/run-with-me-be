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

    def addEvent(self, date, starting_point_long, starting_point_lat, avg_duration, avg_length, avg_pace, admin_id, max_participants):
        #TODO
        created_at = datetime.datetime.now()
        date = datetime.fromtimestamp(date)
        if(avg_pace == None):
            avg_pace = utils.calculateAvgPace(avg_length, avg_duration)

        return 