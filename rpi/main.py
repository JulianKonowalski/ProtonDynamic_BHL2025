from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import db
import buttons

WAIT_AFTER_TEXT = 3  # s

lcd = CharLCD(
    cols=16,
    rows=2,
    pin_rs=26,
    pin_e=19,
    pins_data=[13, 6, 5, 21],
    numbering_mode=GPIO.BCM,
)

reader = SimpleMFRC522()

buttons.setup_button_pins()


def led_set(text: str):
    lcd.clear()
    lcd.write_string(text)


def get_press():
    pressed = None
    while pressed is None:
        pressed = buttons.detect_press()
    return pressed


def user_add_question(rfid):
    while True:
        led_set("Add user? Y-1, N-2")
        pressed = get_press()
        if pressed == 1:
            is_success = db.add_user("Adam", "Chuj", str(rfid))
            if is_success:
                led_set("Added successfully.")
            else:
                led_set("Add failed.")
            break
        if pressed == 2:
            led_set("User add abandoned.")
            break
    time.sleep(WAIT_AFTER_TEXT)


def user_look_for_task(user_unique_id):
    unfinished_tasks = owned_unfinished_tasks(user_unique_id)
    if unfinished_tasks == []:
        choose_task(user_unique_id)
    else:
        update_task_finished(unfinished_tasks)
        led_set("Updated tasks")
        time.sleep(WAIT_AFTER_TEXT)


def update_task_finished(unfinished_tasks: list):
    for task in unfinished_tasks:
        led_set(f"{task['id']}. {task['type'].strip()} finished? Y-1, N-2")
        while True:
            pressed = get_press()
            if pressed == 1:
                db.update_task(task["id"], True, task["owner"])
                break
            elif pressed == 2:
                db.update_task(task["id"], False, None)
                break


def choose_task(user_id):
    todo_tasks = get_tasks_to_do()
    if todo_tasks == []:
        led_set("No tasks to do :c")
        time.sleep(WAIT_AFTER_TEXT)
        return
    chosen = choose_from_list(
        [f"{idx + 1}. {task['type'].strip()}" for idx, task in enumerate(todo_tasks)]
    )
    if chosen is None:
        led_set("Task selection cancelled")
        time.sleep(WAIT_AFTER_TEXT)
        return
    task = todo_tasks[chosen[0]]
    db.update_task(task["id"], False, user_id)
    led_set("Task chosen successfully.")
    time.sleep(WAIT_AFTER_TEXT)


def get_tasks_to_do():
    tasks = db.get_tasks()
    if tasks is None:
        return None
    return [
        task for task in tasks if task["finished"] is False and task["owner"] is None
    ]


def owned_unfinished_tasks(user_id):
    tasks = db.get_tasks()
    if tasks is None:
        return None
    return [
        task for task in tasks if task["finished"] is False and task["owner"] == user_id
    ]


def wait_rfid():
    while True:
        led_set("Waiting for card...")
        id, _ = reader.read()
        user_data = db.get_user(id)
        if user_data is None:
            user_add_question(id)
        else:
            name = user_data["user_name"].strip()
            led_set(f"Good evening, {name}!")
            time.sleep(WAIT_AFTER_TEXT - 1)
            user_look_for_task(user_data["id"])
        time.sleep(WAIT_AFTER_TEXT)


def choose_from_list(items: list[str]):
    curr_idx = 0
    max_idx = len(items) - 1
    print(items)
    led_set(f"{items[curr_idx]}. Select? Y-1, N-2")

    while True:
        press = get_press()
        if press == 1:
            curr_idx = max(curr_idx - 1, 0)
        elif press == 2:
            curr_idx = min(curr_idx, max_idx)
        elif press == 3:
            return curr_idx, items[curr_idx]
        else:
            return None
        led_set(f"{items[curr_idx]}. Select? UP-1, DWN-2, Y-3, N-4")


if __name__ == "__main__":
    lcd.clear()

    try:
        while True:
            try:
                wait_rfid()
                time.sleep(WAIT_AFTER_TEXT)
            except db.DbConnectError:
                led_set("Database access failed.")
                time.sleep(WAIT_AFTER_TEXT)
    finally:
        lcd.clear()
        GPIO.cleanup()
