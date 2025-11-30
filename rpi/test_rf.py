from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()
try:
    print("Place a tag near the reader…")
    id, text = reader.read()
    print("Card ID:", id)
    print("Text on card:", text)
finally:
    GPIO.cleanup()
