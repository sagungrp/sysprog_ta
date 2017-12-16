from pad4pi import rpi_gpio
import time
t = True
string = ''
KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

ROW_PINS = [7, 17, 21, 22] # BCM numbering
COL_PINS = [10, 9, 11, 8] # BCM numbering

factory = rpi_gpio.KeypadFactory()

keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

return_value_temp = -1

def printKey(key):
    global string
    global return_value_temp
    if key == '*':
        string = string[:-1]
    else:
        string = string + key
	print string
    return_value_temp = key

# printKey will be called each time a keypad button is pressed
keypad.registerKeyPressHandler(printKey)

while len(string) <= 4:
    time.sleep(0.1)
    print string
    pass

keypad.cleanup()
