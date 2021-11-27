from flask import Flask
from flask import request
from flask import Response
from flask.globals import request
import logging
import datetime 
 
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
GET_EVENTS = "/events"
GET_EVENT_BY_ID = "/event/<event_id>"
ADD_EVENT = "/event/add"

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
    if(id != None):
        if(int(id) >= 0):
            #3. FORWARD REQUEST TO MIDDLEWARE
            return Response(middleware.getEventById(id), status=200)

    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(ADD_EVENT, methods=['POST'])
def addEvent():

    # 1. CHECK PARAMETERS
    #"id"
    #"created_at"
    #"date"
    #"starting_point_long"
    #"starting_point_lat"
    #"difficulty_level"
    #"avg_pace"
    #"avg_duration"
    #"avg_length"
    #"admin_id"
    #"current_participants"
    #"max_participants"

    # ID needs to be auto-generated inside backend 
    # CREATED AT -> middleware
    
    # DATE check if ok, then middleware will convert 
    date = request.args.get('date', default=None, type=int)

    if(date == None or utils.checkTimeStamp(date)):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # STARTING POINT
    starting_point_long = request.args.get('starting_point_long', default=None, type=float)
    starting_point_lat = request.args.get('starting_point_lat', default=None, type=float)

    if(starting_point_lat == None and starting_point_long == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.check_long(starting_point_long)==False or utils.check_lat(starting_point_lat)==False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_DURATION
    avg_duration = request.args.get('avg_duration', default=None, type=int)
    if(avg_duration == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkAvgDuration() == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_LENGTH
    avg_length = request.args.get('avg_duration', default=None, type=int)
    if(avg_length == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkAvgLength() == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_PACE if not specified in the request, middleware calculates it
    # TODO se cambiamo formato in 2 int per min e sec qua va cambiato
    avg_pace = request.args.get('avg_pace', default=None, type=float)

    # DIFFICULTY LEVEL calculated dinamically
    
    # ADMIN_ID
    admin_id = request.args.get('admin_id', default=None, type=int)
    if(admin_id == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(admin_id < 0):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # CURRENT_PARTICIPANTS 1 perchè lo sto creando io, middleware
    
    # MAX_PARTICIPANTS mi arriva dal frontend, magari controllo che sia entro un limite
    max_participants = request.args.get('max_participants', default=None, type=int)
    if(max_participants == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkMaxParticipants() == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.addEvent(date, starting_point_long, starting_point_lat, avg_duration, avg_length, avg_pace, admin_id, max_participants), status=200)
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
