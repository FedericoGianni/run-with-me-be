from flask import Flask
from flask import request
from flask import Response
from flask.globals import request
import logging
 
from project.dbmysql.DbController import DbController
from project.Middleware import Middleware

# INIT
app = Flask(__name__)
middleware = Middleware()
FORMAT = "%(asctime)s - %(levelname)-5s - %(threadName)-10s - %(name)-8s - %(module)13s:%(lineno)-3s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

# ROUTES
GET_EVENTS = "/events"

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

@app.route("/events", methods=['GET'])
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
        if((lat <= 90 and lat >= -90) and (long <= 180 and long >= -180)):
            #3. FORWARD REQUEST TO MIDDLEWARE
            #return Response("events response test" + " long: " + str(long) + " lat: " + str(lat), status = 200)   
            return Response(middleware.getEvents(long, lat, max_dist_km), status=200)

    return Response("[BAD REQUEST] -90 <= lat <= 90 & -180 <= long <= 180.\nlong: " + str(long) + " lat: " + str(lat), status=400)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
