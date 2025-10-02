import keyboard
from time import sleep

while True:
    print("Press the NumPad '/' …")
    event = keyboard.read_event(suppress=False)      # waits for the key
    print(f"name = {event.name!r}   scan_code = {event.scan_code}")
    sleep(0.5)