from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import socket
import time
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)

# MongoDB URI
app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"

# Retry connection logic
def connect_to_mongo():
    retries = 5
    while retries > 0:
        try:
            mongo = PyMongo(app)
            mongo.cx.server_info()  # Attempt to force connection
            print("Connected to MongoDB!")
            return mongo
        except ServerSelectionTimeoutError:
            retries -= 1
            print(f"MongoDB not ready, retrying... ({retries} retries left)")
            time.sleep(5)  # Wait before retrying
    raise Exception("Failed to connect to MongoDB after several retries")

# Call the retry connection function
mongo = connect_to_mongo()
db = mongo.db

@app.route("/")
def index():
    hostname = socket.gethostname()
    return jsonify(
        message="Welcome to Tasks app! I am running inside {} pod!".format(hostname)
    )

@app.route("/tasks")
def get_all_tasks():
    tasks = db.task.find()
    data = []
    for task in tasks:
        item = {
            "id": str(task["_id"]),
            "task": task["task"]
        }
        data.append(item)
    return jsonify(
        data=data
    )

# Other routes remain the same...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

