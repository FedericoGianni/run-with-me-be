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
import bcrypt

from project.dbmysql.DbParser import DbParser

# ENV VARIABLES
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
        self.__usersTable = Table("users", metadata, autoload=True, autoload_with = self.__engine)
        self.__parser = DbParser()

        #TODO verificare se servono per le transactions
        # create a configured "Session" class
        Session = sessionmaker(bind=self.__engine)
         # create a Session
        self.session = Session()

# EVENTS

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

    def getEventsQuery(self, long, lat, max_dist_km):
        # sqlalchemy query to db
        __connection = self.__engine.connect()

        try:
            
            # TODO: to reduce the computations by the db we should first precompute a rectangle/circle 
            # from starting point and then compute exact distance only for that rectangle
            #
            #query = select([self.__eventsTable]).where(and_(
            #    self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon')
                # self.__eventsTable.c.starting_point_long >= rectangle.get('minLon'), 
                # self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon'), 
                # self.__eventsTable.c.starting_point_long <= rectangle.get('maxLon'), 
            
            #))

            # return only events not already done since we won't delete old events for statistics
            # TODO for performance purposes it should be better to have 2 different tables, one for upcoming events one for old events
            query = select([self.__eventsTable]).where(and_(6371 * func.ACOS(
            func.COS(func.RADIANS(lat))
            * func.COS(func.RADIANS(self.__eventsTable.c.starting_point_lat))
            * func.COS(func.RADIANS(self.__eventsTable.c.starting_point_long) - func.RADIANS(long))
            + func.SIN(func.RADIANS(lat))
            * func.SIN(func.RADIANS(self.__eventsTable.c.starting_point_lat))) <= max_dist_km),
            (self.__eventsTable.c.date >= func.NOW()))

            result = __connection.execute(query).fetchall()

        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        
        __connection.close()
        return result

    def getEvents(self, long, lat, max_dist_km):
        result = self.getEventsQuery(long, lat, max_dist_km)
        return self.__parser.events2Json(result)

    def getEventsAuth(self, long, lat, max_dist_km, user_id):

        events = self.getEventsQuery(long, lat, max_dist_km)
        bookings = self.getBookingsByUserIdQuery(user_id)
        
        # convert query row results to dictionaries
        events = self.__parser.events2OrderedDict(events)
        bookings = self.__parser.bookings2OrderedDict(bookings)

        # add user_booked = true/false to the event dictionary reply
        for event in events:
            event["user_booked"] = False
            for booking in bookings:
                if(event["id"] == booking["event_id"]):
                    logging.info("event: " + str(event["id"]) + " has been booked by user " + str(user_id))
                    event["user_booked"] = True
        
        return self.__parser.eventsDict2Json(events)

    def getEventByIdQuery(self, id):
        __connection = self.__engine.connect()
        try:
            query = select([self.__eventsTable]).where(self.__eventsTable.c.id == id)
            result = __connection.execute(query).fetchall()
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getEventById(self, id):
        return self.__parser.event2Json(self.getEventByIdQuery(id))

    def getEventByIdAuth(self, id, user_id):

        events = self.getEventByIdQuery(id)
        events = self.__parser.events2OrderedDict(events)
        event = events[0]
        bookings = self.getBookingsByUserIdQuery(user_id)
        bookings = self.__parser.bookings2OrderedDict(bookings)

        event["user_booked"] = False
        for booking in bookings:
            if(event["id"] == booking["event_id"]):
                logging.info("event: " + str(event["id"]) + " has been booked by user " + str(user_id))
                event["user_booked"] = True


        
        return self.__parser.eventsDict2Json(event)

    def getEventsByUserId(self, user_id):
        __connection = self.__engine.connect()
        try:
            query = select([self.__eventsTable]).join(self.__bookingsTable, self.__bookingsTable.c.event_id == self.__eventsTable.c.id)\
                .where(self.__bookingsTable.c.user_id == user_id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.events2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getEventsByAdminId(self, admin_id):
        __connection = self.__engine.connect()
        try:
            query = select([self.__eventsTable]).where(self.__eventsTable.c.admin_id == admin_id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.events2Json(result)
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
        newEventId = -1

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

# BOOKINGS

    def checkBookingsFull(self, event_id):
        
        events = self.getEventByIdQuery(event_id)
        events = self.__parser.events2OrderedDict(events)
        event = events[0]

        if(event['current_participants'] == event['max_participants']):
            return True
        return False

    def getBookingsByEventIdQuery(self, event_id):
        __connection = self.__engine.connect()
        try:
            query = select([self.__bookingsTable]).where(self.__bookingsTable.c.event_id == event_id)
            result = __connection.execute(query).fetchall()
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getBookingsByEventId(self, event_id):
        return self.__parser.bookings2Json(self.getBookingsByEventIdQuery(event_id))

    def getBookingsByUserIdQuery(self, user_id):
        __connection = self.__engine.connect()
        try:
            query = select([self.__bookingsTable]).where(self.__bookingsTable.c.user_id == user_id)
            result = __connection.execute(query).fetchall()
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getBookingsByUserId(self, user_id):
        return self.__parser.bookings2Json(self.getBookingsByUserIdQuery(user_id))

    def addBooking(self, booking):
        
        newBookingId = -1
        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                #check that booking from that user for that event has not already made
                query = select(self.__bookingsTable).where(and_(self.__bookingsTable.c.event_id == booking['event_id'], self.__bookingsTable.c.user_id == booking['user_id']))
                result = __connection.execute(query).fetchall()
                logging.info("addBooking checking if booking not already made")
                
                # insert booking only if not already present
                if(not result):
                    i = insert(self.__bookingsTable)
                    i = i.values(booking)
                    newBookingId = self.session.execute(i).inserted_primary_key[0]
                    # increase +1 on current_participants from this event
                    self.session.query(self.__eventsTable).filter(self.__eventsTable.c.id == booking['event_id']).update({'current_participants': self.__eventsTable.c.current_participants + 1})
                    self.session.commit()
                else:
                    newBookingId = result[0].id
                

            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            return e
        __connection.close()

        #should return auto-generated id of the new event
        return self.__parser.bookingId2Json(newBookingId)
        
    def delBooking(self, user_id, event_id):

        __connection = self.__engine.connect()
        
        try:
            with self.session.begin():

                # TODO check if booking exist, otherwise it will decrease participants even if it shouldn't


                # 1 delete booking from bookingswhere
                b = delete(self.__bookingsTable).where(and_(self.__bookingsTable.c.event_id == event_id, self.__bookingsTable.c.user_id == user_id))
                result = self.session.execute(b)
                
                # if rowcount > 0 then it actually deleted booking
                if(result.rowcount > 0):
                # decrease -1 on current_participants from this event
                    self.session.query(self.__eventsTable).filter(self.__eventsTable.c.id == event_id).update({'current_participants': self.__eventsTable.c.current_participants - 1})
                    self.session.commit()
                
                # TODO
                # 2 if no more bookings, delete event? NOT SURE IF NEEDED 
                #i = delete(self.__eventsTable).where(self.__eventsTable.c.id == event_id)
                #self.session.execute(i)
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
        __connection.close()

        return self.__parser.eventId2Json(event_id)

# USERS

    def getUserInfo(self, user_id):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            query = select([self.__usersTable]).where(self.__usersTable.c.id == user_id)
            result = __connection.execute(query).fetchall()
            result = self.__parser.user2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def getUserInfoByUsername(self, username):
        # sqlalchemy query to db
        __connection = self.__engine.connect()
        try:
            query = select([self.__usersTable]).where(self.__usersTable.c.username == username)
            result = __connection.execute(query).fetchall()
            result = self.__parser.user2Json(result)
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

    def addUser(self, user):

        newUserId = -1
        __connection = self.__engine.connect()

        try:
            with self.session.begin():

                i = insert(self.__usersTable)
                i = i.values(user)
                newUserId = self.session.execute(i).inserted_primary_key[0]
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None
        __connection.close()

        #should return auto-generated id of the new user
        return self.__parser.userId2Json(newUserId)

    def updateUser(self, user_id, updatedUser):

        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                i = update(self.__usersTable).where(self.__usersTable.c.id == user_id)
                i = i.values(updatedUser)
                self.session.execute(i)
            
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None
        __connection.close()

        #should return auto-generated id of the new event
        return self.__parser.userId2Json(user_id)

    def delUser(self, user_id):

        # TODO CAPIRE PERCHè DOPO AVER FATTO GETUSERBBYID DI UNO ELIMINATO DA LIST INDEX OUT OF RANGE\

        __connection = self.__engine.connect()
        
        try:
            with self.session.begin():
                b = delete(self.__usersTable).where(self.__usersTable.c.id == user_id)
                self.session.execute(b)

            
        except Exception as e:
            logging.error("{message}.".format(message=e))
        __connection.close()

        return self.__parser.userId2Json(user_id)

    def getUserIdFromUsername(self, username):
        __connection = self.__engine.connect()
        try:
            query = select([self.__usersTable]).where(self.__usersTable.c.username == username)
            result = __connection.execute(query).fetchall()
            result = self.__parser.user2OrderedDict(result[0])
            result = result["id"]
        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
        __connection.close()
        return result

# AUTH

    def checkUserExist(self, username):

        __connection = self.__engine.connect()

        try:
            with self.session.begin():
                # check if username does not already exit
                query = select([self.__usersTable]).where(self.__usersTable.c.username == username)
                result = __connection.execute(query).fetchall()

                logging.info("checkUserExist: " + str(result))
                
                # check if list not empty
                if(result):
                    if(result[0] != None):
                        return True
                                    
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None

        __connection.close()
        return False



    def register(self, newUser):

        newUserId = -1
        __connection = self.__engine.connect()

        # TODO check username già preso
        if(self.checkUserExist(newUser['username'])):
            print("user already exists: " + newUser['username'])
            return self.__parser.userId2Json(newUserId)

        try:
            with self.session.begin():
                    i = insert(self.__usersTable)
                    i = i.values(newUser)
                    newUserId = self.session.execute(i).inserted_primary_key[0]    
                
        except Exception as e:
            logging.error("{message}.".format(message=e))
            result = None
        __connection.close()

        #should return auto-generated id of the new user
        return self.__parser.userId2Json(newUserId)

    def login(self, username, password):
        __connection = self.__engine.connect()

        try:
            query = select([self.__usersTable]).where(self.__usersTable.c.username == username)
            result = __connection.execute(query).fetchall()
            logging.info(result[0])
            result = self.__parser.user2OrderedDictWithPass(result[0])

            logging.info("checking password: " + str(password) + " =?= " + str(result["password"]))
            if bcrypt.checkpw(password.encode('utf-8'), result["password"].encode('utf-8')):
                return True
            else:
                return False

        except Exception as e:
            logging.error("{message}.".format(message=e))
            #result = False, GenericDatabaseError(e)
            result = None
