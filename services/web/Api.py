import logging
import datetime

from flask import Flask
from flask import request
from flask import Response
from flask.globals import request
from flask import jsonify

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

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
GET_EVENTS_AUTH = "/events/auth"
GET_EVENT_BY_ID = "/event/<event_id>"
GET_EVENT_BY_ID_AUTH = "/event/auth/<event_id>"
GET_EVENTS_BY_USER_ID = "/events/user/<user_id>"
GET_EVENTS_BY_ADMIN_ID = "/events/admin/<admin_id>"
ADD_EVENT = "/event/add"
UPDATE_EVENT = "/event/<event_id>"
DELETE_EVENT = "/event/<event_id>"

# BOOKINGS
GET_BOOKINGS_BY_EVENT_ID = "/bookings/event"
GET_BOOKINGS_BY_USER_ID = "/bookings/user"
ADD_BOOKING = "/booking/add"
DELETE_BOOKING = "/booking"

# TODO USERS -> dipende anche da come gestiamo l'autenticazione
# USERS
GET_USER = "/user/id/<user_id>"
GET_USER_BY_USERNAME = "/user/username/<username>"
ADD_USER = "/user/add"
DELETE_USER = "/user/<user_id>"
UPDATE_USER = "/user/<user_id>"

#AUTH
LOGIN = "/login"
REGISTER = "/register"

# FLASK-JWT EXTENDED CONFIG
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# API 
@app.route("/")
def hello_world():
    return "hello", 200

# EVENTS

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
            return Response(middleware.getEvents(long, lat, max_dist_km), status=200, mimetype='application/json')
    
    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(GET_EVENTS_AUTH, methods=['GET'])
@jwt_required()
def getEventsAuth():

    # 1. READ REQUEST
    long = request.args.get('long', default=None, type=float)
    lat = request.args.get('lat', default=None, type=float)
    max_dist_km = request.args.get('max_dist_km', default=50, type=int)
    user_id = get_jwt_identity()
    logging.info("get_jwt_identity: " + str(get_jwt_identity()))

    # 2. CHECK CORRECTNESS OF REQUEST 
    # -90 <= lat <= 90
    # -180 <= long <= 180
    # max_dist_km > 0
    logging.info("[API] received events request. \n long: " + str(long) + " lat: " + str(lat) + " max_dist_km: " + str(max_dist_km))

    if(long != None and lat != None and max_dist_km != None):
        if(utils.checkLat(lat) and utils.checkLong(long)):
            #3. FORWARD REQUEST TO MIDDLEWARE   
            return Response(middleware.getEventsAuth(long, lat, max_dist_km, user_id), status=200, mimetype='application/json')
    
    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(GET_EVENT_BY_ID, methods=['GET'])
def getEventByID(event_id):

    # 1. READ REQUEST
    id = event_id

    # 2. CHECK CORRECTNESS OF REQUEST
    if(utils.checkId(int(id)) == True):
        #3. FORWARD REQUEST TO MIDDLEWARE
        return Response(middleware.getEventById(id), status=200, mimetype='application/json')

    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(GET_EVENT_BY_ID_AUTH, methods=['GET'])
@jwt_required()
def getEventByIDAuth(event_id):

    # 1. READ REQUEST
    id = event_id
    user_id = get_jwt_identity()

    # 2. CHECK CORRECTNESS OF REQUEST
    if(utils.checkId(int(id)) == True):
        #3. FORWARD REQUEST TO MIDDLEWARE
        return Response(middleware.getEventByIdAuth(id, user_id), status=200, mimetype='application/json')

    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(GET_EVENTS_BY_ADMIN_ID, methods=['GET'])
@jwt_required()
def getEventsByAdminId(admin_id):
            
    if(utils.checkId(admin_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getEventsByAdminId(admin_id), status=200, mimetype='application/json')

@app.route(GET_EVENTS_BY_USER_ID, methods=['GET'])
@jwt_required()
def getEventsByUserId(user_id):
            
    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getEventsByUserId(user_id), status=200, mimetype='application/json')

@app.route(ADD_EVENT, methods=['POST'])
@jwt_required()
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

    return Response(middleware.addEvent(event), status=200, mimetype='application/json')

@app.route(DELETE_EVENT, methods=['DELETE'])
@jwt_required()
def deleteEvent(event_id):

    # 1. READ REQUEST
    id = int(event_id)

    # 2. CHECK CORRECTNESS OF REQUEST
    if(id != None):
        if(id >= 0):
            return Response(middleware.deleteEvent(id), status=200, mimetype='application/json')
    
    return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

@app.route(UPDATE_EVENT, methods=['POST'])
@jwt_required()
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
    
    return Response(middleware.updateEvent(event_id, updatedEvent), status=200, mimetype='application/json')

# BOOKINGS

@app.route(GET_BOOKINGS_BY_EVENT_ID, methods=['GET'])
@jwt_required()
def getBookingsByEventId():
    event_id = request.args.get('event_id', default=None, type=int)

    if(utils.checkId(event_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getBookingsByEventId(event_id), status=200, mimetype='application/json')

@app.route(GET_BOOKINGS_BY_USER_ID, methods=['GET'])
@jwt_required()
def getBookingsByUserId():
    user_id = request.args.get('user_id', default=None, type=int)

    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getBookingsByUserId(user_id), status=200, mimetype='application/json')

@app.route(ADD_BOOKING, methods=['POST'])
@jwt_required()
def addBooking():
    
    user_id = request.args.get('user_id', default=None, type=int)
    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    event_id = request.args.get('event_id', default=None, type=int)
    if(utils.checkId(event_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    return Response(middleware.addBooking(user_id, event_id), status=200, mimetype='application/json')

@app.route(DELETE_BOOKING, methods=['DELETE'])
@jwt_required()
def delBooking():

    user_id = request.form.get('user_id', default=None, type=int)
    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    event_id = request.form.get('event_id', default=None, type=int)
    if(utils.checkId(event_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    return Response(middleware.delBooking(user_id, event_id), status=200, mimetype='application/json')

# USERS

@app.route(GET_USER, methods=['GET'])
@jwt_required()
def getUserInfo(user_id):
        
    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getUserInfo(user_id), status=200, mimetype='application/json')

@app.route(GET_USER_BY_USERNAME, methods=['GET'])
@jwt_required()
def getUserInfoByUsername(username):
        
    if(utils.checkUsername(username) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    return Response(middleware.getUserInfoByUsername(username), status=200, mimetype='application/json')

@app.route(ADD_USER, methods=['POST'])
@jwt_required()
def addUser():
    # id -> dbparser
    # name 
    # surname 
    # created_at -> middleware
    # height int
    # age int
    # fitness_level float
    # city

    # 1. CHECK REQUEST

    # NAME AND SURNAME
    name = request.form.get('name', default=None, type=str)
    surname = request.form.get('name', default=None, type=str)
    
    if(name == None or surname == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    if(utils.checkName(name) == False or utils.checkName(surname) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    # HEIGHT
    height = request.form.get('height', default=None, type=int)
        
    if(height == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkHeight(height) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AGE
    age = request.form.get('age', default=None, type=int)
    
    if(age == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkAge(age) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    
    # FITNESS LEVEL
    fitness_level = request.form.get('fitness_level', default=None, type=float)
    
    if(fitness_level == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkFitnessLevel(fitness_level) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # CITY
    city = request.form.get('city', default=None, type=str)
    
    if(city == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    if(utils.checkCity(city) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    
    user = {
        "name": name,
        "surname": surname,
        "height": height,
        "age": age,
        "fitness_level": fitness_level,
        "city": city,
    }

    return Response(middleware.addUser(user), status=200, mimetype='application/json')

@app.route(UPDATE_USER, methods=['POST'])
@jwt_required()
def updateUser(user_id):
    # NOTE: differently from addUser, parameters can be None

    # 1. CHECK REQUEST

    # NAME AND SURNAME
    name = request.form.get('name', default=None, type=str)
    surname = request.form.get('surname', default=None, type=str)

    if(name != None):
        if(utils.checkName(name) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    if(surname != None):
        if(utils.checkName(surname) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    # HEIGHT
    height = request.form.get('height', default=None, type=int)
        
    if(height != None):
        if(utils.checkHeight(height) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # AGE
    age = request.form.get('age', default=None, type=int)
    
    if(age != None):
        if(utils.checkAge(age) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    
    # FITNESS LEVEL
    fitness_level = request.form.get('fitness_level', default=None, type=float)
    
    if(fitness_level != None):
        if(utils.checkFitnessLevel(fitness_level) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    # CITY
    city = request.form.get('city', default=None, type=str)
    
    if(city != None):
        if(utils.checkCity(city) == False):
            return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)

    user = {
        "name": name,
        "surname": surname,
        "height": height,
        "age": age,
        "fitness_level": fitness_level,
        "city": city,
    }

    return Response(middleware.updateUser(user_id, user), status=200, mimetype='application/json')

@app.route(DELETE_USER, methods=['DELETE'])
@jwt_required()
def delUser(user_id):

    if(user_id == None):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400) 
    if(utils.checkId(user_id) == False):
        return Response(errors.GENERIC_BAD_REQUEST_ERROR, status=400)
    
    return Response(middleware.delUser(user_id), status=200, mimetype='application/json')

# AUTH 

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route(LOGIN, methods=["POST"])
def login():
    username = request.form.get('username', default=None, type=str)
    password = request.form.get('password', default=None, type=str)

    if(middleware.login(username, password)):
        user_id = middleware.getUserIdFromUsername(username)
        logging.info("getting user_id from username: " + str(username) + "->" + str(user_id))
        access_token = create_access_token(identity=user_id, expires_delta=datetime.timedelta(days=3))
        return jsonify(access_token=access_token, user_id=user_id), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route(REGISTER, methods=["POST"])
def register():
    #TODO
    username = request.form.get('username', default=None, type=str)
    password = request.form.get('password', default=None, type=str)
    return Response(middleware.register(username, password), status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
