import json
import enum
import dotenv
from flask import Flask, request, make_response

from database.Influx import Influxdb 
from database.Postgres import Postgres

class AuthLevel(enum.Enum):
    ADMIN = 0
    SENSOR = 1
    USER = 2

dotenv.load_dotenv()

app: Flask = Flask(__name__)
influx: Influxdb = Influxdb()
postgres: Postgres = Postgres()

def authenticate(api_key: str) -> dict | None:
    if not api_key: return None
    user_data: dict = postgres.getUserData(api_key)
    if not user_data: return None
    return user_data

def authorize(user_data: dict, auth_level: AuthLevel) -> bool:
    try: return user_data["role_id"] < auth_level.value
    except KeyError: return False

@app.route("/create_user", methods=["POST"])
def createUser():
    data = request.get_json()
    if not data: make_response("Bad request", 400)

    try: postgres.createUser(data["user_name"], data["user_surname"], data["rfid"])
    except KeyError: return make_response("Bad request", 400)

    return make_response("Ok", 200)

@app.route("/get_user", methods=["GET"])
def getUserData():
    data = request.get_json()
    if not data: return make_response("Bad request", 400)

    try: user_data = postgres.getUserData(data["rfid"])
    except KeyError: return make_response("Bad request", 400)

    return app.response_class(
        response=json.dumps({"data": user_data}),
        status=200,
        mimetype="application/json"
    )

@app.route("/update_task", methods=["POST"])
def updateTask():
    data = request.get_json()
    if not data: return make_response("Bad request", 400)

    try: owner = data["owner"]
    except KeyError: owner = None

    try: postgres.updateTask(data["task_id"], data["finished"], owner)
    except KeyError: return make_response("Bad request", 400)

    return make_response("Ok", 200)

@app.route("/get_tasks", methods=["GET"])
def getTasks():
    return app.response_class(
        response=json.dumps({"data", postgres.getTasks()}),
        status=200,
        mimetype="application/json"
    )

@app.route("/upload", methods=["POST"])
def upload():
    user_data: dict | None = authenticate(request.headers.get("Authorization"))
    if not user_data: return make_response("Unauthorized access", 401)
    if not authorize(user_data, AuthLevel.SENSOR): return make_response("Forbidden access", 403)

    data = request.get_json()
    influx.writeRecord(data["sensor_id"], data["temperature"], data["humidity"])
    return app.response_class(
        response=json.dumps({"data": data}),
        status=200,
        mimetype="application/json"
    )

@app.route("/get", methods=["GET"])
def get():
    user_data: dict | None = authenticate(request.headers.get("Authorization"))
    if not user_data: return make_response("Unauthorized access", 401)

    data = request.get_json()
    return app.response_class(
        response=json.dumps({"data": influx.readRecords(data["duration"])}),
        status=200,
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)