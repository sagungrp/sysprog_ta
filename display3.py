from RPLCD import CharLCD
import RPi.GPIO as GPIO
import time

from pad4pi import rpi_gpio


pins_data=[18, 23, 24, 25]
pin_e=7
pin_rs=8

# Setup Keypad
KEYPAD = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
]

COL_PINS = [7,17,21,22] # BCM numbering
ROW_PINS = [10,9,11,8] # BCM numbering


factory = rpi_gpio.KeypadFactory()

keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

global key_handler
global var
string = ""
nomor_sepeda = ""
confirm = ""


def processPK(key):
    var = False
    global string
    string = key

def processConfirm(key):
    global confirm
    confirm = key

def processType(key):
    # Loop while waiting for a keypress
    global nomor_sepeda
    if key == '*':
       nomor_sepeda = nomor_sepeda[:-1]
    else:
       nomor_sepeda = nomor_sepeda + key

def pinjam():
    print(u"Nomor Sepeda?")
    global nomor_sepeda
    key_handler = keypad.registerKeyPressHandler(processType)
    while len(nomor_sepeda) < 5:
        time.sleep(0.3)
        print(nomor_sepeda)
    print("Pnjm Spd " + nomor_sepeda + "?")
    print("1:Ya 2:No")
    key_handler = keypad.registerKeyPressHandler(processConfirm)
    global confirm
    yeay = True
    while(yeay and (confirm!="5" or confirm!="2")):
        if(confirm == "2"):
            print("Yay terpinjam")
            time.sleep(5)
            yeay = False
        elif(confirm == "5"):
            pinjam()
            yeay = False


def kembali():
    print("kembali")

def wait_input(switch):
    while not GPIO.input(switch):
        time.sleep(0.2)

while True:
    print("Pinjam/Kembali?")
    print("1:P 2:K 3:Back")
    key_handler = keypad.registerKeyPressHandler(processPK)
    string = ""
    while len(string) < 1:
        time.sleep(0.3)
        print(string)
    if(string == "2"):
        pinjam()
    elif (string =="5"):
        kembali()
    else:
        print("Salah Pencet")

    global confirm
    global nomor_sepeda
    global string
    confirm = ""
    nomor_sepeda = ""
    string = ""
