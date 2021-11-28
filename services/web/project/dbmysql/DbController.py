import datetime
from flask.globals import request
from sqlalchemy.orm.util import CascadeOptions
from sqlalchemy.sql.expression import *
from sqlalchemy import create_engine, MetaData, Table, and_, event, true
from sqlalchemy.orm import query, sessionmaker
import logging
from geopy import distance
from geopy.distance import geodesic
import geopy


from project.dbmysql.DbParser import DbParser

DB_TYPE = 'mysql+pymysql'
DB_USER = 'hello_flask'
DB_PASSWORD = 'hello_flask'
DB_ADDRESS = 'db:3306'
DB_NAME = 'hello_flask_prod'

class DbController():

    session = None

    def __init__(self):
        self.__engine = create_engine(DB_TYPE+"://"+DB_USER+":"+DB_PASSWORD+"@"+DB_ADDRESS+"/"+DB_NAME, pool_pre_ping=True)
        metadata = MetaData()
        self.__eventsTable = Table("events", metadata, autoload = True, autoload_with = self.__engine)
        self.__bookingsTable = Table("bookings", metadata, autoload = True, autoload_with = self.__engine)
        self.__parser = DbParser()

        #TODO verificare se servono per le transactions
        # create a configured "Session" class
        Session = sessionmaker(bind=self.__engine)
         # create a Session
        self.session = Session()

    # EXAMPLE
    # def geteventsUser(self):
    #     """
    #     A method that returns a list of complete device objects, queried from the database with a specific user permission
    #     :return: the list of complete device object
    #     """

    #     __connection = self.__engine.connect()
    #     try:
    #         query = select([self.__eventsTable]).select_from().where(and_(self.__eventsTable.c.client_uuid == [0], self.__eventsTable.c.is_deleted == False))
    #         result = __connection.execute(query).fetchall()
    #         result = self.__event2Json(result)
    #     except Exception as e:
    #         logging.error("{message}.".format(message=e))
    #         result = False, GenericDatabaseError(e)
    #     __connection.close()
    #     return result

    def calc_rectangle(self, long, lat, max_dist_km):
        result_dict = {
            "minLat": 0.0,
            "maxLat": 0.0,
            "minLon": 0.0,
            "maxLon": 0.0,
        }

        # return list (minLat, maxLat, minLon, maxLon) from starting point
        # define starting point. 
        start = geopy.Point(lat, long)

        # define a general distance object, initialized with a distance of max_dist_km 
        d = geopy.distance.distance(kilometers = max_dist_km)
        # dse the `destination` method with a bearing of 0 degrees (which is north)
        # in order to go from point `start` max_dist_km km to north.
        # bearing (float) – Bearing in degrees: 0 – North, 90 – East, 180 – South, 270 or -90 – West.

        #maxLat
        result_dict['maxLat'] = d.destination(point=start, bearing=0)[0]
        print('lat: ' + str(lat))
        print('maxLat: ' + str(result_dict.get('maxLat')))
        #minLat
        result_dict['minLat'] = d.destination(point=start, bearing=180)[0]
        print('lat: ' + str(lat))
        print('minLat: ' + str(result_dict.get('minLat')))
        #maxLon
        result_dict['maxLon'] = d.destination(point=start, bearing=90)[1]
        print('lon: ' + str(long))
        print('maxLon: ' + str(result_dict.get('maxLon')))
        #minLon 
        result_dict['minLon'] = d.destination(point=start, bearing=-90)[1]
        print('lon: ' + str(long))
        print('minLon: ' + str(result_dict.get('minLon')))
        
        return result_dict

    def getEvents(self, lat, long, max_dist_km):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            #TODO return only events within max_dist_km from starting point (rectangle)
            starting_point = (lat, long)
            rectangle = self.calc_rectangle(lat, long, max_dist_km)
            #TODO long e lat possono anche essere negative 
            query = select([self.__eventsTable]).where(and_(
                self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon')
                # self.__eventsTable.c.starting_point_long >= rectangle.get('minLon'), 
                # self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon'), 
                # self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon'), 
            
            ))
            result = __connection.execute(query).fetchall()
            result = self.__parser.events2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getEventById(self, id):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            query = select([self.__eventsTable]).where(self.__eventsTable.c.id == id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.event2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    #TODO capire se fa una transaction cosi o no
    def addEvent(self, event):
        booking = {
            "created_at": event['created_at'],
            "user_id": event['admin_id'],
            "event_id": 0,
        }
        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                # TODO verificare se così fa una transaction o cosa
                # 1 add new event to events
                # 2 add admin_id to the bookings for that event 
                
                i = insert(self.__eventsTable)
                i = i.values(event)
                newEventId = self.session.execute(i).inserted_primary_key[0]

                booking['event_id'] = newEventId
                i = insert(self.__bookingsTable)
                i = i.values(booking)
                self.session.execute(i)
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None
        __connection.close()

        #should return auto-generated id of the new event
        return self.__parser.eventId2Json(newEventId)

    def deleteEvent(self, event_id):

        __connection = self.__engine.connect()
        
        try:
            with self.session.begin():
                # TODO verificare se così fa una transaction o cosa
                # 1 add new event to events
                # 2 add admin_id to the bookings for that event 
                b = delete(self.__bookingsTable).where(self.__bookingsTable.c.event_id == event_id)
                self.session.execute(b)
                
                i = delete(self.__eventsTable).where(self.__eventsTable.c.id == event_id)
                self.session.execute(i)
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
        __connection.close()

        return self.__parser.eventId2Json(event_id)
        
    def updateEvent(self, event_id, updatedEvent):

        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                i = update(self.__eventsTable)
                i = i.values(updatedEvent)
                self.session.execute(i)
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None
        __connection.close()

        #should return auto-generated id of the new event
        return self.__parser.eventId2Json(event_id)

    def getBookingsByEventId(self, event_id):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            query = select([self.__bookingsTable]).where(self.__bookingsTable.c.event_id == event_id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.bookings2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getBookingsByUserId(self, user_id):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            query = select([self.__bookingsTable]).where(self.__bookingsTable.c.user_id == user_id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.bookings2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def addBooking(self, booking):

        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                i = insert(self.__bookingsTable)
                i = i.values(booking)
                newBookingId = self.session.execute(i).inserted_primary_key[0]
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            return e
        __connection.close()

        #should return auto-generated id of the new event
        return self.__parser.bookingId2Json(newBookingId)
