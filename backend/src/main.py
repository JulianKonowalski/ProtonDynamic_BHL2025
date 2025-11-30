import os
import json
import enum
import dotenv
import pathlib
from flask import Flask, request, make_response
from flask_cors import CORS

from database.Influx import Influxdb 
from database.Postgres import Postgres
from werkzeug.utils import secure_filename

RCV_PATH: str = os.path.join(pathlib.Path(__file__).parent.resolve(), "..", "rcv")

class AuthLevel(enum.Enum):
    ADMIN = 0
    SENSOR = 1
    USER = 2

dotenv.load_dotenv()

app: Flask = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

CORS(app)

influx: Influxdb = Influxdb()
postgres: Postgres = Postgres()

def authenticateUser(rfid: str) -> dict | None:
    if not rfid: return None
    user_data: dict | None = postgres.getUserData(rfid)
    if not user_data: return None
    return user_data

def authenticateSensor(api_key: str) -> dict | None:
    if not api_key: return None
    sensor_data: dict | None = postgres.getSensorData(api_key)
    if not sensor_data: return None
    return sensor_data

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

    if not user_data: return make_response("User not found", 404)
    return app.response_class(
        response=json.dumps({"data": user_data}),
        status=200,
        mimetype="application/json"
    )

@app.rout('/update_sc', methods=["POST"])
def updateSC():
    data = request.get_json()
    if not data: return make_response("Bad request", 400)

    try: postgres.addUserCredit(data["social_credit"])
    except KeyError: return make_response("Bad request", 400)

    return make_response("Ok", 200)

@app.route("/update_task", methods=["POST"])
def updateTask():
    data = request.get_json()
    if not data: return make_response("Bad request", 400)

    try: owner = data["owner"]
    except KeyError: owner = None

    try: postgres.updateTask(data["task_id"], data["finished"], owner)
    except KeyError: return make_response("Bad request", 400)

    return make_response("Ok", 200)

@app.route("/get_task_types", methods=["GET"])
def getTaskTypes():
    return app.response_class(
        response=json.dumps({"data": postgres.getTaskTypes()}),
        status=200,
        mimetype="application/json"
    )

@app.route("/get_tasks", methods=["GET"])
def getTasks():
    return app.response_class(
        response=json.dumps({"data": postgres.getTasks()}),
        status=200,
        mimetype="application/json"
    )

@app.route("/upload", methods=["POST"])
def upload():
    sensor_data: dict | None = authenticateSensor(request.headers.get("Authorization"))
    if not sensor_data: return make_response("Unauthorized access", 401)

    data = request.get_json()

    if data["humidity"] < 40:
        tasks = postgres.getTasks()
        latch = False
        for task in tasks:
            if task["type"] == 2 and not task["finished"]: 
                latch = True
                break
        if not latch: postgres.createTask(2)

    influx.writeRecord(data["sensor_id"], data["temperature"], data["humidity"])
    return app.response_class(
        response=json.dumps({"data": data}),
        status=200,
        mimetype="application/json"
    )

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image received", 400

    file = request.files['image']

    if file.filename == '':
        return "Empty filename", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f"Saved {filename}", 200

    return "Invalid file", 400

@app.route("/get", methods=["GET"])
def get():
    data = influx.readRecords("1m")
    return app.response_class(
        response=json.dumps({"data": data}),
        status=200,
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)