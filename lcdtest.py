from RPLCD import CharLCD
import RPi.GPIO as GPIO
import time

from pad4pi import rpi_gpio


pins_data=[9, 10, 22, 21]
pins_data2=[21,22,10,9]
pin_e=11
pin_rs=7

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_rs, GPIO.OUT)
GPIO.setup(pin_e, GPIO.OUT)
for pin in pins_data:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, True)

lcd = CharLCD(cols=16, rows=2, pin_rs=7, pin_e=11, pins_data=[9, 10, 21, 22], numbering_mode=GPIO.BCM)

lcd.cursor_pos = (0,0)
lcd.write_string(u'Pinjam/Kembali?')
lcd.cursor_pos = (1,0)
lcd.write_string(u'1:P 2:K 3:Back')
time.sleep(5)
lcd.clear()
GPIO.cleanup()
