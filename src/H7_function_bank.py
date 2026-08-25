from machine import UART
import re

#define variables below
encoder_count = 0
wheel_revolutions = 0
tof0 = 0
tof1 = 0

uart = UART(1, 115200)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1) #sets additional settings
buf = b"" # create empty byte object and assigns it to variable 'buf' (short for buffer)
pattern = re.compile(r'encoder count:\s*(\d+),\s*tof0:\s*(\d+),\s*tof1:\s*(\d+)') #for UART parsing

def read_UART():
    if uart.any() > 0: #if UART recieves any data:
        buf += uart.read(uart.any())  # grab everything currently waiting
        if b'\n' in buf: #if byte containing \n (newline indicator) is in the buffer:
            line_byte, buf = buf.split(b'\n', 1)  # split off the first complete line
            line_string = line_byte.decode('utf-8').strip() #convert line from bytes to string, remove whitespace
            match = pattern.search(line_string) #search for the pattern in the string. integers are stored in match.groups
            if match:
                #assign values to variables:
                encoder_count = int(match.group(1))
                tof0 = int(match.group(2))
                tof1 = int(match.group(3))
                wheel_rotations = encoder_count // (28*3) #divide by 28, since 7PPR encoder has 28 counts per rev. divide by 3, since gear ratio is 1:3
            print(f"Parsed -> Encoder: {encoder_count}, TOF0: {tof0}, TOF1: {tof1}")
        else:
            print("Failed to parse string structure")

# EXAMPLE OF line_byte when printed ---- b'encoder count: 1250, tof0: 3400, tof1: 42\r'
# EXAMPLE OF line_string ---- 'encoder count: 1250, tof0: 3400, tof1: 42'
            
            







# This program set up an I2C connection to the BNO08i device
# Then Create a BNO08i class based object
# Then enables sensors
# And finallj report sensors everj 0.5 seconds.
from machine import I2C, Pin
from utime import ticks_ms, sleep_ms
import math
from bno08x import *

i2c1 = I2C(2, freq=100000, timeout=200000 ) #i2c2 = 4 scl, 5 sda

bno = BNO08X(i2c1, debug=False)
print("BNO08x I2C connection : Done\n")

bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR, 10) #enable game rotation vector (no magnetometer) report
bno.set_quaternion_euler_vector(BNO_REPORT_GAME_ROTATION_VECTOR) 

print("BNO08x sensors enabling : Done\n")

cpt = 0 #set counter to 0

def read_IMU():
    #time.sleep(0.5)
    cpt += 1
    print("cpt", cpt)
    R, T, P = bno.euler
    print("Euler Angle\tX: {:+.3f}\tY: {:+.3f}\tZ: {:+.3f}".format(R, T, P))
    if cpt == 10 : #TARES AT THE 10TH LOOP
        bno.tare #Tareing: resets R,T,P to 0,0,0
        
        
        
        


from machine import PWM, Pin

servo = PWM(Pin("P7"), freq=50, duty_ns=1_500_000)  # centre

def set_position(angle):
    # angle: 0..180 degrees mapped to 1.0..2.0 ms
    pulse_us = 1000 + (angle * 1000) // 180
    servo.duty_ns(pulse_us * 1000)

#EXAMPLES
#set_position(25)	# full right
#set_position(135)    # full left
#set_position(80)     # centre





import time
from machine import PWM, Pin

dir_pin = Pin("P9", Pin.OUT)
speed = PWM(Pin("P8"), freq=20_000, duty_u16=0)

def drive(direction, speed_percent):
    dir_pin.value(direction)         # 0 or 1
    speed.duty_u16((speed_percent*65535)//100)     # duty cycle goes from 0..65535, speed_percent scales to 1-100

#EXAMPLES
#drive(0, 100)     # direction A at full speed
#drive(1, 50)     # direction B at half speed

#BRAKING?
#speed.duty_u16(0)   # stop








        
        
        
        
        
        




