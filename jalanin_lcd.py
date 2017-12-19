import lcd_driver as lcd
from time import *

mylcd = lcd.lcd()

while True:
    mylcd.lcd_display_string("Hello ", 1)
    sleep(1)
    mylcd.backlight(1)
