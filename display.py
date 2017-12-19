from RPLCD import CharLCD
import RPi.GPIO as GPIO
import time
import MFRC522
import signal
from pad4pi import rpi_gpio
import requests
import json
import lcd_driver as lcd

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

my_lcd = lcd.lcd()



# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
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
peminjaman = None

def clear_variable():
    global option
    global pinjam_option
    global nomor_sepeda
    global confirm_pinjam_sepeda_flag
    global nomor_sepeda_finish_flag
    global global_uid 

    option = 0
    pinjam_option = 0
    nomor_sepeda = 0
    confirm_pinjam_sepeda_flag = 0
    nomor_sepeda_finish_flag = 0
    global_uid = ''
    peminjaman = None

def getCardDataFromServer(uid):
    global jwt_token

    url = "http://azurarestapi.herokuapp.com/api/peminjamans/" + uid

    headers = {
        'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVhMzg4YWFiYTg2ZTg2MDAxNDY3MmQzMSIsImlhdCI6MTUxMzY4MTI0NX0.duSg8e2ZZhm8EMkvK_dzEFgRsGrhlQ8sSIFZ6M-fNMM",
        'cache-control': "no-cache",
        'postman-token': "611c9049-a317-84d4-20a4-1386b1551adf"
    }

    response = requests.request("GET", url, headers=headers)
    return response


def sendDataToServer(data):
    global jwt_token
    url = "https://azurarestapi.herokuapp.com/api/peminjamans"

    payload = data
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'authorization': jwt_token,
        'cache-control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return response


def sendDataToServerKembali(data):
    global jwt_token
    url = "https://azurarestapi.herokuapp.com/api/peminjamans"

    payload = data
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'authorization': jwt_token,
        'cache-control': "no-cache",
    }
    response = requests.request("PUT", url, data=payload, headers=headers)
    return response

def processKeyOption(key):
    global option
    if key.isdigit():
        option = int(key)

def processNomorSepedaKey(key):
    global nomor_sepeda
    if key.isdigit():
        nomor_sepeda = nomor_sepeda * 10 + int(key)
        my_lcd.lcd_display_string(key, 2, len(str(nomor_sepeda))-1)

def processNomorSepedaKeyDelete(key):
    global nomor_sepeda
    if(len(str(nomor_sepeda)) >= 1 and key == "D"):
        nomor_sepeda = nomor_sepeda / 10
        my_lcd.lcd_display_string('', 2, len(str(nomor_sepeda))-1)

def processPinjamSepedaConfirmKey(key):
    global confirm_pinjam_sepeda_flag
    if(key == "1" or key == "2"):
        confirm_pinjam_sepeda_flag = int(key)

def processNomorSepedaFinishedFlag(key):
    global nomor_sepeda_finish_flag
    if(key == "A"):
        nomor_sepeda_finish_flag = 1

def pinjam():
    keypad.clearKeyPressHandlers()
    keypad.registerKeyPressHandler(processNomorSepedaKey)
    keypad.registerKeyPressHandler(processNomorSepedaFinishedFlag)
    keypad.registerKeyPressHandler(processNomorSepedaKeyDelete)
    global nomor_sepeda
    global confirm_pinjam_sepeda_flag
    my_lcd.lcd_display_string("Nomor Sepeda?", 1)
    while nomor_sepeda_finish_flag == 0:
        time.sleep(0.1)
        pass
    keypad.clearKeyPressHandlers()
    my_lcd.lcd_clear()
    my_lcd.lcd_display_string("Pnjm Spd " + str(nomor_sepeda) + "?", 1)
    my_lcd.lcd_display_string("1:Ya 2:No", 2)
    keypad.registerKeyPressHandler(processPinjamSepedaConfirmKey)
    while confirm_pinjam_sepeda_flag != 1 and confirm_pinjam_sepeda_flag != 2:
        pass
    #lcd.clear()
    if(confirm_pinjam_sepeda_flag == 1):
        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        global global_uid
        global NAMA_STASIUN_PINJAM
        data = ""
        data = data + "uidMahasiswa=" + global_uid + '&stasiunPinjam=' + NAMA_STASIUN_PINJAM + "&nomorSepeda=" + str(nomor_sepeda)
        my_lcd.lcd_clear()
        my_lcd.lcd_display_string("Loading", 1)
        response = sendDataToServer(data)
        if(response.status_code == 200):
            my_lcd.lcd_clear()
            my_lcd.lcd_display_string("Silahkan Ambil", 1)
            my_lcd.lcd_display_string("Sepeda", 2)
            global continue_reading
            continue_reading = False
            time.sleep(4)
        elif(response.status_code == 404):
            my_lcd.lcd_clear()
            my_lcd.lcd_display_string("Selamat Meminjam", 1)
        clear_variable()
    elif(confirm_pinjam_sepeda_flag == 2):
        clear_variable()
        pinjam()

def kembali():
    global peminjaman
    global global_uid
    global NAMA_STASIUN_BALIK
    data = ""
    data = data + "uidMahasiswa=" + global_uid + '&stasiunBalik=' + NAMA_STASIUN_BALIK
    my_lcd.lcd_clear()
    my_lcd.lcd_display_string("Loading", 1)
    response = sendDataToServerKembali(data)
    # print "Sending data to server"
    if(response.status_code == 200):
        my_lcd.lcd_clear()
        my_lcd.lcd_display_string("Sepeda " + str(peminjaman['nomorSepeda']), 1)
        my_lcd.lcd_display_string("Dikembalikan", 2)
        global continue_reading
        continue_reading = False
        time.sleep(1)
    elif(response.status_code == 404):
        my_lcd.lcd_clear()
        my_lcd.lcd_display_string("Selamat Meminjam", 1)
    clear_variable()

while True:
    continue_reading = True
    my_lcd.lcd_clear()
    my_lcd.lcd_display_string("Silahkan Tap", 1)
    my_lcd.lcd_display_string("Kartu Anda", 2)
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
                my_lcd.lcd_clear()
                response = getCardDataFromServer(global_uid)
                if(response.status_code == 200):
                    global peminjaman
                    peminjaman = json.loads(response.text)
                    if peminjaman['statusPinjam']:
                        kembali()
                    else:
                        pinjam()
                elif(response.status_code == 404):
                    pinjam()
                else:
                    print "An error occured"

                MIFAREReader.MFRC522_Read(8)
                MIFAREReader.MFRC522_StopCrypto1()
            else:
                print "Authentication error"




