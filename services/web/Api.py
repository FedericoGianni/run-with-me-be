from flask import Flask
from project.db.DbController import DbController


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5005')
    DbController()
