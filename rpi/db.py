import requests
import json

IP = "http://10.88.2.66:5000"
REQUEST_TIMEOUT = 1  # s

header = {"Content-Type": "application/json"}


class DbConnectError(Exception):
    pass


def get_user(rfid: str):
    url = IP + "/get_user"
    payload = {"rfid": rfid}
    try:
        response = requests.get(
            url, headers=header, data=json.dumps(payload), timeout=REQUEST_TIMEOUT
        )
    except:
        raise DbConnectError()
    if response.status_code == 200:
        return response.json()["data"]
    return None


def add_user(name: str, surname: str, rfid: str) -> bool:
    url = IP + "/create_user"
    payload = {"user_name": name, "user_surname": surname, "rfid": rfid}
    try:
        response = requests.post(
            url, headers=header, data=json.dumps(payload), timeout=REQUEST_TIMEOUT
        )
    except:
        raise DbConnectError()
    if response.status_code == 200:
        return True
    return False


def get_tasks():
    url = IP + "/get_tasks"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except:
        raise DbConnectError()
    if response.status_code == 200:
        return response.json()["data"]
    return None


def get_task_types():
    url = IP + "/get_task_types"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except:
        raise DbConnectError()
    if response.status_code == 200:
        return response.json()["data"]
    return None


def update_task(task_id: int, finished: bool, owner_id: int | None = None):
    url = IP + "/update_task"
    payload = {"owner": owner_id, "task_id": task_id, "finished": finished}
    try:
        response = requests.post(
            url, headers=header, data=json.dumps(payload), timeout=REQUEST_TIMEOUT
        )
    except:
        raise DbConnectError()
    if response.status_code == 200:
        return True
    return False
