from flask import Flask
from flask import request
from flask import Response
from flask.globals import request
import logging
import datetime

from sqlalchemy import event 
 
from project.dbmysql.DbController import DbController
from project.Middleware import Middleware
import ApiHelpers as utils
import ApiErrors as errors

# INIT
app = Flask(__name__)
middleware = Middleware()
FORMAT = "%(asctime)s - %(levelname)-5s - %(threadName)-10s - %(name)-8s - %(module)13s:%(lineno)-3s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

# ROUTES

# EVENTS
GET_EVENTS = "/events"
GET_EVENT_BY_ID = "/event/<event_id>"
ADD_EVENT = "/event/add"
UPDATE_EVENT = "/event/<event_id>"
DELETE_EVENT = "/event/<event_id>"

# BOOKINGS
GET_BOOKINGS = "/bookings"
ADD_BOOKING = "/booking/add"


# API 
@app.route("/")
def hello_world():
    return "hello", 200

# EXAMPLE
@app.route("/register/<message>", methods=['GET'])
def register(message=False):
    # check on correctness of request
    # call to middleware
    if message:
        middleware.register(message)
    pass

@app.route(GET_EVENTS, methods=['GET'])
def getEvents():

    # 1. READ REQUEST
    long = request.args.get('long', default=None, type=float)
    lat = request.args.get('lat', default=None, type=float)
    max_dist_km = request.args.get('max_dist_km', default=50, type=int)
    
    # 2. CHECK CORRECTNESS OF REQUEST 
    # -90 <= lat <= 90
    # -180 <= long <= 180
    # max_dist_km > 0
    logging.info("[API] received events request. \n long: " + str(long) + " lat: " + str(lat) + " max_dist_km: " + str(max_dist_km))

    if(long != None and lat != None and max_dist_km != None):
        if(utils.checkLat(lat) and utils.checkLong(long)):
            #3. FORWARD REQUEST TO MIDDLEWARE   
            return Response(middleware.getEvents(long, lat, max_dist_km), status=200)
    
    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(GET_EVENT_BY_ID, methods=['GET'])
def getEventByID(event_id):

    # 1. READ REQUEST
    id = event_id

    # 2. CHECK CORRECTNESS OF REQUEST
    if(utils.checkId(int(id)) == True):
        #3. FORWARD REQUEST TO MIDDLEWARE
        return Response(middleware.getEventById(id), status=200)

    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(ADD_EVENT, methods=['POST'])
def addEvent():

    # 1. CHECK PARAMETERS 
    # CREATED AT -> middleware
    
    # DATE check if ok, then middleware will convert 
    date = request.form.get('date', default=None, type=int)

    if(date == None):
        logging.info("BAD REQUEST: date is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkTimeStamp(date) == False):
        logging.info("BAD REQUEST: date format wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # NAME
    name = request.form.get('name', default=None, type=str)

    if(name == None):
        logging.info("BAD REQUEST: name is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkEventName(name) == False):
        logging.info("BAD REQUEST: event name format wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400) 


    # STARTING POINT
    starting_point_long = request.form.get('starting_point_long', default=None, type=float)
    starting_point_lat = request.form.get('starting_point_lat', default=None, type=float)

    if(starting_point_lat == None or starting_point_long == None):
        logging.info("BAD REQUEST: lat and/or long is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkLong(starting_point_long)==False or utils.checkLat(starting_point_lat)==False):
        logging.info("BAD REQUEST: lat and/or long format is wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_DURATION
    avg_duration = request.form.get('avg_duration', default=None, type=int)
    if(avg_duration == None):
        logging.info("BAD REQUEST: avg_duration is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkAvgDuration(avg_duration) == False):
        logging.info("BAD REQUEST: avg_duration format is wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_LENGTH
    avg_length = request.form.get('avg_length', default=None, type=int)
    if(avg_length == None):
        logging.info("BAD REQUEST: avg_length is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkAvgLength(avg_length) == False):
        logging.info("BAD REQUEST: avg_length format is wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_PACE if not specified in the request, middleware calculates it
    # TODO se cambiamo formato in 2 int per min e sec qua va cambiato
    avg_pace_min = request.form.get('avg_pace_min', default=None, type=float)
    avg_pace_sec = request.form.get('avg_pace_sec', default=None, type=float)
    
    if(avg_pace_min != None and avg_pace_sec != None):
        if(utils.checkAvgPace(avg_pace_min, avg_pace_sec) == False):
            logging.info("BAD REQUEST: avg_pace_min and/or avg_pace_sec is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # DIFFICULTY LEVEL calculated dinamically by middleware
    
    # ADMIN_ID
    admin_id = request.form.get('admin_id', default=None, type=int)
    if(admin_id == None):
        logging.info("BAD REQUEST: admin_id is none")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(admin_id < 0):
        logging.info("BAD REQUEST: admin_id format is wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # CURRENT_PARTICIPANTS 1 perchè lo sto creando io, middleware
    
    # MAX_PARTICIPANTS mi arriva dal frontend, magari controllo che sia entro un limite
    max_participants = request.form.get('max_participants', default=None, type=int)
    if(max_participants == None):
        logging.info("BAD REQUEST: max_participants is None")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkMaxParticipants(max_participants) == False):
        logging.info("BAD REQUEST: max_participants format is wrong")
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    event = {
        "date": date,
        "name": name,
        "starting_point_long" : starting_point_long,
        "starting_point_lat": starting_point_lat,
        "avg_pace_min" : avg_pace_min,
        "avg_pace_sec" : avg_pace_sec,
        "avg_duration" : avg_duration,
        "avg_length" : avg_length,
        "admin_id" : admin_id,
        "max_participants" : max_participants
    }

    return Response(middleware.addEvent(event), status=200)

@app.route(DELETE_EVENT, methods=['DELETE'])
def deleteEvent(event_id):

    # 1. READ REQUEST
    id = int(event_id)

    # 2. CHECK CORRECTNESS OF REQUEST
    if(id != None):
        if(id >= 0):
            return Response(middleware.deleteEvent(id), status=200)
    
    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(UPDATE_EVENT, methods=['POST'])
def updateEvent(event_id):

    # NOTE: differently from addEvent, parameters can be None

    # 1. CHECK PARAMETERS
    if(utils.checkId(int(event_id)) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # DATE
    date = request.form.get('date', default=None, type=int)
    if(date != None):
        if(utils.checkTimeStamp(date) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)            
    
    # NAME
    name = request.form.get('name', default=None, type=str)
    if(name != None):
        if(utils.checkEventName(name) == False):
            logging.info("BAD REQUEST: event name format wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400) 

    # STARTING POINT LONG
    starting_point_long = request.form.get('starting_point_long', default=None, type=float)
    if(starting_point_long != None):
        if(utils.checkLat(starting_point_long) == False):
            logging.info("BAD REQUEST: long format wrong")

    # STARTING POINT LAT
    starting_point_lat = request.form.get('starting_point_lat', default=None, type=float)
    if(starting_point_lat != None):
        if(utils.checkLat(starting_point_lat)==False):
            logging.info("BAD REQUEST: lat format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)    
    
    # AVG PACE MIN
    avg_pace_min = request.form.get('avg_pace_min', default=None, type=int)
    if(avg_pace_min != None):
        if(utils.checkAvgPaceMin(avg_pace_min) == False):
            logging.info("BAD REQUEST: avg_pace_min format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG PACE SEC
    avg_pace_sec = request.form.get('avg_pace_sec', default=None, type=int)
    if(avg_pace_sec != None):
        if(utils.checkAvgPaceSec(avg_pace_sec) == False):
            logging.info("BAD REQUEST: avg_pace_sec format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_DURATION
    avg_duration = request.form.get('avg_duration', default=None, type=int)
    if(avg_duration != None):
        if(utils.checkAvgDuration(avg_duration) == False):
            logging.info("BAD REQUEST: avg_duration format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_LENGTH
    avg_length = request.form.get('avg_length', default=None, type=int)
    if(avg_length != None):
        if(utils.checkAvgLength(avg_length) == False):
            logging.info("BAD REQUEST: avg_length format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    # ADMIN_ID
    admin_id = request.form.get('admin_id', default=None, type=int)
    if(admin_id != None):
        if(admin_id < 0):
            logging.info("BAD REQUEST: admin_id format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    # MAX_PARTICIPANTS
    max_participants = request.form.get('max_participants', default=None, type=int)
    if(max_participants != None):
        if(utils.checkMaxParticipants(max_participants) == False):
            logging.info("BAD REQUEST: max_participants format is wrong")
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)    
    
    updatedEvent = {
        "date": date,
        "name": name,
        "starting_point_long" : starting_point_long,
        "starting_point_lat": starting_point_lat,
        "avg_pace_min" : avg_pace_min,
        "avg_pace_sec" : avg_pace_sec,
        "avg_duration" : avg_duration,
        "avg_length" : avg_length,
        "admin_id" : admin_id,
        "max_participants" : max_participants
    }
    
    return Response(middleware.updateEvent(event_id, updatedEvent), status=200)

@app.route(GET_BOOKINGS, methods=['GET'])
def getBookingsByEventId():
    event_id = request.args.get('event_id', default=None, type=int)

    if(utils.checkId(event_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getBookingsByEventId(event_id), status=200)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
