from machine import UART, I2C, Pin, PWM
import re
from utime import ticks_ms, sleep_ms
import math
from bno08x import *
import time
from pid import PID



#loop counter (not just for imu)
global cpt = 0
#for uart
global uart = None
global buf = None
#for imu
global bno = None
global tare = False
#for servo
global servo = None
#for motor driver
global dir_pin = None
global speed = None

#LAB thresholds, roi
global roi_line = (0, 0, cw, ch//2)   # ROI for line detection (check irl)
global orange_t = (2, 0, 0, 0, 0, 0)
global blue_t = (3,0,0,0,0,0)

def find_blue():
    global blue_t, roi_line
    blue_blobs = img.find_blobs([blue_t], x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
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


def find_orange():
    global orange_t, roi_line
    orange_blobs = img.find_blobs([orange_t], roi=roi_line, x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
    if orange_blobs:
        b = orange_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        cx = b.cx
        cy = b.cy
        w = b.w
        h = b.h
        rot = b.rotation
        print(cx, cy, w, h, rot)
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
            print("Failed to parse string structure")
        
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

    
def read_imu():
    #time.sleep(0.5)
    global cpt, tare_status
    print("cpt", cpt)
    R, T, P = bno.euler #roll, tilt, pan euler angle
    # print("Euler Angle\tX: {:+.3f}\tY: {:+.3f}\tZ: {:+.3f}".format(R, T, P))
    print("heading = ", P)
    if cpt == 10 : #TARES AT THE 10TH LOOP
        bno.tare #Tareing: resets R,T,P to 0,0,0
        tare = True
    return P

def init_servo():
    global servo = PWM(Pin("P7"), freq=50, duty_ns=1_500_000)  # centre
    
def set_position(angle):
    # angle: 0..180 degrees mapped to 1.0..2.0 ms
    pulse_us = 1000 + (angle * 1000) // 180
    servo.duty_ns(pulse_us * 1000)

#EXAMPLES
#set_position(25)	# full right
#set_position(135)    # full left
#set_position(80)     # centre
    

def init_driver():
    global dir_pin = Pin("P9", Pin.OUT)
    global speed = PWM(Pin("P8"), freq=20_000, duty_u16=0)

def drive(direction, speed_percent):
    dir_pin.value(direction)         # 0 or 1
    speed.duty_u16((speed_percent*65535)//100)     # duty cycle goes from 0..65535, speed_percent scales to 1-100

#EXAMPLES
#drive(0, 100)     # direction A at full speed
#drive(1, 50)     # direction B at half speed

#BRAKING?
#speed.duty_u16(0)   # stop

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
csi0.window([0, 0, cw, ch])  # leave width as is, crop height to 50% (check irl)
csi0.snapshot(time=2000)  # skip csi0.snapshot for 2000ms for sensor to stabilise

# peripherals init
init_uart()
init_imu()
init_servo()
init_driver()


#setup pid controllers (TUNE THE GAINS)
kp = 1
ki = 1
kd = 1
imu_pid = PID(p=kp, i=ki, d=kd, imax=69)
kp1 = 1
ki1 = 1
kd1 = 1
cam_pid = PID(p=kp1, i=ki1, d=kd1, imax=67)

setpoint_heading = 0
base_setpoint_heading = 0
l_dmin_count = 0
r_dmin_count = 0
#turn state
CW = False

while true:
    cpt+=1  #counter

    #get data
    if tare = True:
        heading = read_imu()
    l_tof = read_uart()[0]  #left TOF
    r_tof = read_uart()[1]  #right TOF
    encoder = read_uart()[2]  #encoder count
    wheel_rot = read_uart()[3] #wheel rotations
    orange = find_orange() #gives orange blob object
    blue = find_blue() #gives blue blob object
    
#go straight
    if l_tof <= dmin:
        l_dmin_count +=1
        if l_dmin_count == 15:
            base_setpoint_heading = setpoint_heading
            setpoint_heading += 5
    else:
        setpoint_heading = base_setpoint_heading
        l_dmin_count = 0

    if r_tof <= dmin:
        r_dmin_count +=1
        if r_dmin_count == 15:
            base_setpoint_heading = setpoint_heading
            setpoint_heading -= 5
    else:
        setpoint_heading = base_setpoint_heading
        r_dmin_count = 0
    imu_error = setpoint_heading - heading
    output = imu_pid.get_pid(imu_error, 1) #second input is the scaling factor applied to the gains
    servo_angle = 80 + output  #servo centred at 80  # scale output as needed to get the servo angle
    set_position(servo_angle)
    drive(0, 100)

    
    
    
    
    



