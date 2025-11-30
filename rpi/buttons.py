import RPi.GPIO as GPIO

rows = [2, 3]  # your row pins
cols = [17, 27]  # your column pins
key_map = [[1, 2], [3, 4]]

def setup_button_pins() -> None:
    GPIO.setmode(GPIO.BCM)
    for c in cols:
        GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for r in rows:
        GPIO.setup(r, GPIO.OUT)
        GPIO.output(r, GPIO.HIGH)


def detect_press() -> int | None:
    for r_index, r in enumerate(rows):
        # Activate this row
        GPIO.output(r, GPIO.LOW)

        for c_index, c in enumerate(cols):
            if GPIO.input(c) == GPIO.LOW:  # active-low press
                GPIO.output(r, GPIO.HIGH)
                return key_map[r_index][c_index]

        # Deactivate the row
        GPIO.output(r, GPIO.HIGH)
    return None
