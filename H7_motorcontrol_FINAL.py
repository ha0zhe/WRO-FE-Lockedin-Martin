import time
from machine import PWM, Pin

dir_pin = Pin("P7", Pin.OUT)
speed = PWM(Pin("P9"), freq=20_000, duty_u16=0)

def drive(direction, speed_percent):
    dir_pin.value(direction)         # 0 or 1
    speed.duty_u16((speed_percent*65535)//100)     # duty cycle goes from 0..65535, speed_percent scales to 1-100

drive(0, 100)     # direction A at full speed
time.sleep(1)
drive(1, 50)     # direction B at half speed
time.sleep(1)
speed.duty_u16(0)   # stop
