from flask import Flask
from flask import request
from flask import Response
from flask.globals import request
 
from project.dbmysql.DbController import DbController
from project.Middleware import Middleware

app = Flask(__name__)
middleware = Middleware()

GET_EVENTS = "/events"

@app.route("/")
def hello_world():
    return "hello", 200

@app.route(GET_EVENTS, methods=['GET'])
def getEvents():
    #check the correctness of req
    long = request.args.get('long')
    lat = request.args.get('lat')
    
    if(long != None and lat != None):
        #call to middleware
        return Response("events response test" + " long: " + long + " lat: " + lat, status = 200)   
        #return Response(middleware.getEvents(long, lat), status=200)
    return Response("bad request", status=400)


@app.route("/register/<message>", methods=['GET'])
def register(message=False):
    # check on correctness of request
    # call to middleware
    if message:
        middleware.register(message)
    pass

#@app.route("/register/<message>", methods=['POST'])
#def register():
#    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
