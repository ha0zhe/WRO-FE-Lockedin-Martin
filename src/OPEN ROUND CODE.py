from machine import UART, I2C, Pin, PWM
import re
from utime import ticks_ms, sleep_ms
import math
from bno08x import *
import time
from pid import PID
import csi



#loop counter (not just for imu)
global cpt
#for uart
global uart
uart= None
global buf
buf = None
#for imu
global bno
bno = None
#for servo
global servo
servo = None
#for motor driver
global dir_pin
dir_pin = None
global speed_pin
speed_pin = None

def find_blue(img, blue_t):
    blue_blobs = img.find_blobs([blue_t], x_stride=4, y_stride=4, area_threshold=2000, merge=True)
    b = None
    if blue_blobs:
        b = blue_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        blue_cx = b.cx
        blue_cy = b.cy
        blue_w = b.w
        blue_h = b.h
        blue_rot = b.rotation
        print(blue_cx, blue_cy, blue_w, blue_h, blue_rot)
    return b

def find_orange(img, orange_t):
    orange_blobs = img.find_blobs([orange_t], x_stride=4, y_stride=4, area_threshold=2000, merge=True)
    b = None
    if orange_blobs:
        b = orange_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        orange_cx = b.cx
        orange_cy = b.cy
        orange_w = b.w
        orange_h = b.h
        orange_rot = b.rotation
        print(orange_cx, orange_cy, orange_w, orange_h, orange_rot)
    return b





def init_uart():
    global uart, buf
    uart = UART(1, 115200)                         # init with given baudrate
    uart.init(115200, bits=8, parity=None, stop=1) #sets additional settings
    buf = b"" # create empty byte object and assigns it to variable 'buf' (short for buffer)

def read_uart():
    global buf
    pattern = re.compile(r'encoder count:\s*(\d+),\s*tof0:\s*(\d+),\s*tof1:\s*(\d+)') #for UART parsing
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
                return tof0, tof1, encoder_count, wheel_rotations
        else:
            print("no valid data")
            return None
# EXAMPLE OF line_byte when printed ---- b'encoder count: 1250, tof0: 3400, tof1: 42\r'
# EXAMPLE OF line_string ---- 'encoder count: 1250, tof0: 3400, tof1: 42'


def init_imu():
    global bno
    i2c1 = I2C(2, freq=100000, timeout=200000 ) #i2c2 = 4 scl, 5 sda
    bno = BNO08X(i2c1, debug=False)
    print("BNO08x I2C connection : Done\n")
    bno.enable_feature(BNO_REPORT_GAME_ROTATION_VECTOR, 10) #enable game rotation vector (no magnetometer) report
    bno.set_quaternion_euler_vector(BNO_REPORT_GAME_ROTATION_VECTOR)
    print("BNO08x sensors enabling : Done\n")


def read_imu(tare_state):
    #time.sleep(0.5)
    global cpt
    print("cpt", cpt)
    R, T, P = bno.euler #roll, tilt, pan euler angle
    # print("Euler Angle\tX: {:+.3f}\tY: {:+.3f}\tZ: {:+.3f}".format(R, T, P))
    print("heading = ", P)
    if cpt == 10 : #TARES AT THE 10TH LOOP
        bno.tare #Tareing: resets R,T,P to 0,0,0
        tare_state = True
    return P, tare_state

def init_servo():
    global servo
    servo = PWM(Pin("P7"), freq=50, duty_ns=1_500_000)  # centre

def set_position(angle):
    # angle: 0..180 degrees mapped to 1.0..2.0 ms
    pulse_us = 1000 + int((angle * 1000) // 180)
    servo.duty_ns(pulse_us * 1000)

#EXAMPLES
#set_position(25)	# full right
#set_position(135)    # full left
#set_position(80)     # centre


def init_driver():
    global dir_pin
    dir_pin = Pin("P9", Pin.OUT)
    global speed_pin
    speed_pin = PWM(Pin("P6"), freq=20_000, duty_u16=0)

def drive(direction, speed_percent):
    dir_pin.value(direction)         # 0 fwd, 1 reverse
    speed_pin.duty_u16((speed_percent*65535)//100)     # duty cycle goes from 0..65535, speed_percent scales to 1-100

#EXAMPLES
#drive(0, 100)     # direction A at full speed
#drive(1, 50)     # direction B at half speed

#BRAKING?
#speed.duty_u16(0)   # stop



def control_loop(wall_avoidance, heading, setpoint_heading, base_setpoint_heading, left_tof, right_tof, left_dmin, right_dmin, left_dmin_count, right_dmin_count, pid_object):
    error = setpoint_heading - heading
    error = (setpoint_heading - heading + 180) % 360 - 180 #normalise to -180 to 180
    output = pid_object.get_pid(error, 1) #second input is the scaling factor applied to the gains
    servo_angle = 80 + output  #servo centred at 80
    servo_angle = max(15, min(145, servo_angle))#clamping to keep servo_angle within range of motion of 15 to 145.
    if wall_avoidance == False:
        base_setpoint_heading = setpoint_heading
    if left_tof <= left_dmin:
        right_dmin_count = 0
        left_dmin_count +=1
        if left_dmin_count == 3:
            wall_avoidance = True
            setpoint_heading -= 10
    elif right_tof <= right_dmin:
        left_dmin_count = 0
        right_dmin_count +=1
        if right_dmin_count == 3:
            wall_avoidance = True
            setpoint_heading += 10
    else:
        wall_avoidance = False
        left_dmin_count = 0
        right_dmin_count = 0
        setpoint_heading = base_setpoint_heading
    return wall_avoidance, servo_angle, left_dmin_count, right_dmin_count, setpoint_heading, base_setpoint_heading

l_tof, r_tof, encoder, wheel_rot = 200, 200, 0, 0 #placeholder before UART data comes in
#setup pid controllers (TUNE THE GAINS)
kp = 1
ki = 0.00
kd = 0
imu_pid = PID(p=kp, i=ki, d=kd, imax=69)
l_dmin_count = 0
r_dmin_count = 0
l_dmin = 100
r_dmin = 100
stpt_hdg = 0
base_stpt_hdg = 0

#tare state
tared = False
#control loop
wall_avoidance = False
#turn state
clockwise = False
counterclockwise = False
turn_count = 0
straight_speed = 50
turn_speed = 50
orange_count = 0
blue_count = 0
speed = 0
#end state
last_section = False

#LAB thresholds, roi
orange_t = (0, 58, -8, 127, 12, 55)
blue_t = (0, 46, -8, 5, -32, -11)

# camera setup
clock = time.clock()
csi0 = csi.CSI()
csi0.reset()
csi0.pixformat(csi.RGB565)
csi0.framesize(csi.QVGA)
csi0.vflip(True)
csi0.hmirror(True)
sw = csi0.width()  # sensor width (in pixels)
sh = csi0.height()  # sensor height
cw = sw  # cropped width
ch = sh//2  # cropped height
roi_line = (0, 0, cw, ch)   # ROI for line detection (check irl)
csi0.window([0, ch, cw, ch])  # leave width as is, crop height to 50% (check irl)
csi0.snapshot(time=2000)  # skip csi0.snapshot for 2000ms for sensor to stabilise
cpt = 0

# peripherals init
init_uart()
init_imu()
init_servo()
init_driver()

button = Pin("P2", Pin.IN, Pin.PULL_UP) #start button, connect between P5 and GND
start = False
if button.value() == 0:
    start = True
else:
    start = False

while not start:
    cpt+=1  #counter
    img = csi0.snapshot()
    #get data
    hdg, tared = read_imu(tared)
    uart_data = read_uart()
    if uart_data:
        (l_tof, r_tof, encoder, wheel_rot) = uart_data  #left TOF, right TOF, encoder count, wheel rotations
    orange = find_orange(img, orange_t) #gives orange blob object
    blue = find_blue(img, blue_t) #gives blue blob object

#driving
    if tared:
        stpt_hdg = stpt_hdg % 360
        print("stpt_hdg: ", stpt_hdg)
        (wall_avoidance, angle, l_dmin_count, r_dmin_count, stpt_hdg, base_stpt_hdg) = control_loop(wall_avoidance, hdg, stpt_hdg, base_stpt_hdg, l_tof, r_tof, l_dmin, r_dmin, l_dmin_count ,r_dmin_count, imu_pid)
        set_position(angle)
        print("angle: ", angle)
        drive(0, speed)

#turning
    if not counterclockwise:
        if orange:
            orange_count += 1
            if orange_count == 3: #so 1 rogue frame wont trigger the turn sequence
                clockwise = True
                counterclockwise = False
                stpt_hdg = stpt_hdg - 90
                turn_count += 1
                speed = turn_speed
        else:
            orange_count = 0
            speed = straight_speed

    if not clockwise:
        if blue:
            blue_count += 1
            if blue_count == 3:
                counterclockwise = True
                clockwise = False
                stpt_hdg = stpt_hdg + 90
                turn_count += 1
                speed = turn_speed
        else:
            blue_count = 0
            speed = straight_speed

#end sequence
    if not last_section:
        start_encoder = encoder
    if turn_count == 12:
        last_section = True
        encoder_change = encoder - start_encoder
        speed = straight_speed // 2
        if encoder_change >= 200:
            speed = 0






