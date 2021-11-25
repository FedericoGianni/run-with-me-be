import logging

from project.dbmysql.DbController import DbController

class Middleware():
    def __init__(self) -> None:
        self.dbController = DbController()
        pass

    def register(self, message):
        pass

    def getEvents(self, long, lat, max_dist_km):
        logging.log(level=logging.INFO, msg="[MIDDLEWARE] long: " + str(long) + " lat: " + str(lat) + " max_dist_km: " + str(max_dist_km))
        events = self.dbController.getEvents(long, lat, max_dist_km)
        return events