from flask import Flask
from project.dbmysql.DbController import DbController
from Middleware import Middleware

app = Flask(__name__)
middleware = Middleware()

@app.route("/")
def hello_world():
    return "hello", 200

@app.route("/register/<message>", methods=['GET'])
def register(message=False):
    # check on correctness of request
    # call to middleware
    if message:
        middleware.register(message)

@app.route("/register/<message>", methods=['POST'])
def register():
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
