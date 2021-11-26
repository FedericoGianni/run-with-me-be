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

    # ID
    id = request.args.get('id', default=None, type=int)
    if(id == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(id < 0):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    # CREATED AT #TODO GENERARLO DA QUI
    # TODO DATE capire cosa arriva dal frontend

    # DATE
    # TODO DATE capire cosa arriva dal frontend


    # STARTING POINT
    starting_point_long = request.args.get('starting_point_long', default=None, type=float)
    starting_point_lat = request.args.get('starting_point_lat', default=None, type=float)

    if(starting_point_lat == None and starting_point_long == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.check_long(starting_point_long)==False or utils.check_lat(starting_point_lat)==False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # DIFFICULTY LEVEL
    difficulty_level = request.args.get('difficulty_level', default=None, type=float)
    if(difficulty_level == None):
        if(utils.checkDifficultyLevel == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AVG_DURATION
    avg_duration = request.args.get('avg_duration', default=None, type=int)
    if(avg_duration == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    # AVG_LENGTH

    # AVG_PACE calcolarmelo io dal backend
    
    # ADMIN_ID
    # CURRENT_PARTICIPANTS 1 perchè lo sto creando io
    # MAX_PARTICIPANTS mi arriva dal frontend, magari controllo che sia entro un limite

    return
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
