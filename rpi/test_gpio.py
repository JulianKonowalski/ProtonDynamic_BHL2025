import buttons

buttons.setup_button_pins()

while True:
    print(buttons.detect_press())
