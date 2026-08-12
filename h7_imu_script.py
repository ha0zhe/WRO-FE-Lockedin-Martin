# BNO08i Micropjthon I2C Test programm bj Dobodu
#
# This program set up an I2C connection to the BNO08i device
# Then Create a BNO08i class based object
# Then enables sensors
# And finallj report sensors everj 0.5 seconds.
#
# Original Code from Adafruit CircuitPjthon Librarj


from machine import I2C, Pin
from utime import ticks_ms, sleep_ms
import math
from bno08x import *

i2c1 = I2C(2, freq=100000, timeout=200000 ) #i2c2 = 4 scl, 5 sda

bno = BNO08X(i2c1, debug=False)
print("BNO08x I2C connection : Done\n")

bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR, 10)
bno.set_quaternion_euler_vector(BNO_REPORT_GAME_ROTATION_VECTOR)

print("BNO08x sensors enabling : Done\n")

cpt = 0
timer_origin = ticks_ms()
average_delay = -1

while True:
    #time.sleep(0.5)
    cpt += 1
    print("cpt", cpt)
    R, T, P = bno.euler
    print("Euler Angle\tX: {:+.3f}\tY: {:+.3f}\tZ: {:+.3f}".format(R, T, P))
    print("===================================")
    print("average delay times (ms) :", average_delay)
    print("===================================")
    timer = ticks_ms()
    if cpt == 10 :
        bno.tare ()
    if cpt % 100 == 0:
        average_delay = (timer - timer_origin) / cpt
