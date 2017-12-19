from RPLCD import CharLCD
import RPi.GPIO as GPIO
import time
import MFRC522
import signal
from pad4pi import rpi_gpio
import requests
import json

# Getting JWT Token
url = "http://azurarestapi.herokuapp.com/api/auth"

payload = "access_token=o2O1JVW8WMy20UtizkzneumvGE1F33ym"
headers = {
    'content-type': "application/x-www-form-urlencoded",
    'authorization': "Basic cml6cXlmYWlzaGFsMjdAZ21haWwuY29tOnBhc3N3b3Jk",
    'cache-control': "no-cache",
    'postman-token': "f1a80315-d24c-1612-bdd9-bcd1a60d4841"
}

response = requests.request("POST", url, data=payload, headers=headers)
jwt_token = 'Bearer ' + json.loads(response.text)['token']

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


NAMA_STASIUN_PINJAM = "Balairung"
NAMA_STASIUN_BALIK = "Fakultas Teknik"

# Setup PIN GPIO
#pins_data=[23, 18, 24, 15]
#pin_e=22
#pin_rs=20

GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin_e, GPIO.OUT)
#GPIO.setup(pin_rs, GPIO.OUT)
#for pin in pins_data:
 #   GPIO.setup(pin, GPIO.OUT)

# Setup Keypad
KEYPAD = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
]

COL_PINS = [23,24,25,7] # BCM numbering
ROW_PINS = [18,17,21,22] # BCM numbering


factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
#lcd = CharLCD(cols=16, rows=2, pin_rs=pin_rs, pin_e=pin_e, pins_data=pins_data, numbering_mode=GPIO.BCM)

# Setup Global Variable

option = 0
pinjam_option = 0
nomor_sepeda = 0
confirm_pinjam_sepeda_flag = 0
nomor_sepeda_finish_flag = 0

global_uid = ''

def sendDataToServer(data):

    global jwt_token
    url = "http://azurarestapi.herokuapp.com/api/peminjamans"

    payload = data
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'authorization': jwt_token,
        'cache-control': "no-cache",
        'postman-token': "80b6c5f7-9546-e304-50c7-c6e6379b20ae"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return response

def processKeyOption(key):
    global option
    if key.isdigit():
        option = int(key)

def processNomorSepedaKey(key):
    global nomor_sepeda
    if key.isdigit():
        nomor_sepeda = nomor_sepeda * 10 + int(key)
        print key

def processNomorSepedaKeyDelete(key):
    global nomor_sepeda
    if(key == "D"):
        nomor_sepeda = nomor_sepeda / 10

def processPinjamSepedaConfirmKey(key):
    global confirm_pinjam_sepeda_flag
    if(key == "1" or key == "2"):
        confirm_pinjam_sepeda_flag = int(key)

def processNomorSepedaFinishedFlag(key):
    global nomor_sepeda_finish_flag
    if(key == "A"):
        nomor_sepeda_finish_flag = 1

def pinjam():
    keypad.clearKeyPressHandler()
    keypad.registerKeyPressHandler(processNomorSepedaKey)
    keypad.registerKeyPressHandler(processNomorSepedaFinishedFlag)
    keypad.registerKeyPressHandler(processNomorSepedaKeyDelete)

    #lcd.cursor_pos = (0,0)
    #lcd.write_string(u"Nomor Sepeda?")
    print "Nomor Sepeda?"
    while nomor_sepeda_finish_flag == 0:
        time.sleep(0.1)
        pass
    #lcd.clear()
    #lcd.cursor_pos = (0,0)
    #lcd.write_string("Pnjm Spd " + no_sepeda + "?")
    keypad.clearKeyPressHandler()
    print "Pnjm Spd " + no_sepeda + "?"
    #lcd.cursor_pos = (1,0)
    #lcd.write_string("1:Ya 2:No")
    print "1:Ya 2:No"
    keypa.registerKeyPressHandler(processPinjamSepedaConfirmKey)
    while confirm_pinjam_sepeda_flag != 1 or confirm_pinjam_sepeda_flag != 2:
        pass
    #lcd.clear()
    if(confirm_pinjam_sepeda_flag == 1):
        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        data = ""
        data = data + "uidMahasiswa=" + global_uid + '&stasiunPinjam=' + NAMA_STASIUN_PINJAM + "&noSepeda=" + nomor_sepeda
        response = sendDataToServer(data)
        print "Sending data to server"
        if(response.status_code == 200):
            lcd.write_string("Yay terpinjam")
            print "Yay terpinjam"
            global continue_reading
            continue_reading = false
            time.sleep(1)
    elif(confirm_pinjam_sepeda_flag == 2):
        pinjam()

def wrong_button(text_up, text_down):
    #lcd.clear()
    #lcd.cursor_pos = (0,0)
    #lcd.write_string("Teken yg bener!")
    #time.sleep(3)
    #lcd.clear()
    #lcd.cursor_pos = (0,0)
    #lcd.write_string(text_up)
    #lcd.cursor_pos = (1,0)
    #lcd.write_string(text_down)
    pass

def kembali():
    server_kirim()
 
def wait_input(switch):
    while not GPIO.input(switch):
        time.sleep(0.01)

while True:
    continue_reading = True
    print "Silahkan Tap Kartu Anda"
    while continue_reading:
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        # If a card is found
        # if status == MIFAREReader.MI_OK:
        #     print "Card detected"
                
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            # print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            global_uid = str(uid[0])+":"+str(uid[1])+":"+str(uid[2])+":"+str(uid[3])
            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
                    
            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                MIFAREReader.MFRC522_Read(8)
                MIFAREReader.MFRC522_StopCrypto1()
                keypad.registerKeyPressHandler(processKeyOption)
                #lcd.cursor_pos = (0,0)
                #lcd.write_string("Pinjam/Kembali?")
                #print "Pinjam/Kembali?"
                #lcd.cursor_pos = (1,0)
                #lcd.write_string("1:P 2:K")
                #print "1:P 2:K 3:Back"
                #lcd.clear()
                print "Pinjam/Kembali?"
                print "1:P 2:K"
                while option == 0:
                    pass
                if(option == 1):
                    pinjam()
                elif (option == 2):
                    kembali()
            else:
                print "Authentication error"




