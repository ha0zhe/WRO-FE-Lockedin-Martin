# ============================================================
# WRO 2026 FUTURE ENGINEERS
# OBSTACLE CHALLENGE
#
# COMPLETE PYTHON CONTROL PROGRAM
#
# Existing hardware ports are UNCHANGED:
#
# UART          = UART(1)
# IMU           = I2C(2)
# Servo         = P8
# Motor DIR     = P9
# Motor PWM     = P6
#
# ============================================================


# ============================================================
# ORIGINAL UART CODE
# ============================================================

from machine import UART
import re


# define variables below

encoder_count = 0
wheel_revolutions = 0
tof0 = 0
tof1 = 0


uart = UART(1, 115200)

uart.init(
    115200,
    bits=8,
    parity=None,
    stop=1)


buf = b""


pattern = re.compile(
    r'encoder count:\s*(\d+),\s*'
    r'tof0:\s*(\d+),\s*'
    r'tof1:\s*(\d+)')


def read_UART():

    global buf, encoder_count, tof0, tof1, wheel_revolutions

    if uart.any() > 0:

        buf += uart.read(
            uart.any())

        if b'\n' in buf:

            line_byte, buf = buf.split(b'\n',1)

            line_string = (line_byte.decode('utf-8').strip())

            match = pattern.search(line_string)

            if match:

                encoder_count = int(match.group(1))

                tof0 = int(match.group(2))

                tof1 = int(match.group(3))

                wheel_rotations = (encoder_count/(28 * 3))

            print("Parsed -> Encoder:",encoder_count,"TOF0:",tof0,"TOF1:",tof1)

        else:

            print("Failed to parse string structure")


# ============================================================
# ORIGINAL IMU CODE
# ============================================================

from machine import I2C, Pin
from utime import ticks_ms, ticks_diff, sleep_ms
import math
from bno08x import *


i2c1 = I2C(
    2,
    freq=100000,
    timeout=200000
)


bno = BNO08X(
    i2c1,
    debug=False
)


print(
    "BNO08x I2C connection : Done\n"
)


bno.enable_feature(
    BNO_REPORT_GAME_ROTATION_VECTOR,
    10
)


bno.set_quaternion_euler_vector(
    BNO_REPORT_GAME_ROTATION_VECTOR
)


print(
    "BNO08x sensors enabling : Done\n"
)


cpt = 0


def read_IMU():

    global cpt

    cpt += 1

    print(
        "cpt",
        cpt
    )

    R, T, P = bno.euler

    print(
        "Euler Angle\tX: {:+.3f}\tY: {:+.3f}\tZ: {:+.3f}".format(
            R,
            T,
            P
        )
    )

    if cpt == 10:

        bno.tare()


# ============================================================
# ORIGINAL SERVO CODE
# ============================================================

from machine import PWM, Pin


servo = PWM(
    Pin("P8"),
    freq=50,
    duty_ns=1_500_000)


def set_position(angle):

    pulse_us = (
        1000
        +
        (angle * 1000)
        //
        180)

    servo.duty_ns(
        pulse_us * 1000)


# Existing examples:
#
# set_position(25)   full right
# set_position(135)  full left
# set_position(80)   centre


# ============================================================
# ORIGINAL MOTOR CODE
# ============================================================

import time
from machine import PWM, Pin


dir_pin = Pin(
    "P9",
    Pin.OUT
)


speed = PWM(
    Pin("P6"),
    freq=20_000,
    duty_u16=0
)


def drive(
    direction,
    speed_percent
):

    dir_pin.value(
        direction
    )

    speed.duty_u16(
        (
            speed_percent
            *
            65535
        )
        //
        100
    )


# ============================================================
#
# NEW WRO OBSTACLE CHALLENGE CODE STARTS HERE
#
# ============================================================


import sensor


# ============================================================
# MOTOR DIRECTION
# ============================================================

FORWARD = 0
REVERSE = 1


# ============================================================
# STEERING
# =========================S===================================

STEERING_RIGHT = 25
STEERING_CENTRE = 80
STEERING_LEFT = 135


MAX_BLOB_STEERING = 40

MAX_IMU_STEERING = 35


# ============================================================
# SPEEDS
# ============================================================

# Slow parking/start speed to reduce wheel slip

LEAVING_SPEED = 50

NORMAL_SPEED =70

AVOID_SPEED = 60

TURN_SPEED = 65

PARKING_SPEED = 60


# ============================================================
# WHEEL / ENCODER
# ============================================================

ENCODER_COUNTS_PER_REV = (
    28 * 3
)


# CHANGE THIS
# Measure your actual wheel diameter

WHEEL_DIAMETER_MM = 34


WHEEL_CIRCUMFERENCE_MM = (
    math.pi
    *
    WHEEL_DIAMETER_MM
)


# ============================================================
# ROUND SETTINGS
# ============================================================

ROUND_TIME_LIMIT_MS = (
    3 * 60 * 1000
)


TARGET_LAPS = 3

TURNS_PER_LAP = 4


# Distance travelled after fourth corner
# before confirming that the lap is complete.

LAP_CONFIRM_DISTANCE_MM = 150


# ============================================================
# LEAVING PARKING LOT
# ============================================================

BACKUP_DISTANCE_MM = 40


RIGHT_TURN_TIME_MS = 900

STRAIGHT_CLEAR_TIME_MS = 800

LEFT_TURN_TIME_MS = 900


# ============================================================
# TOF
# ============================================================

# Change to False if tof0 is physically on RIGHT

TOF0_IS_LEFT = True


WALL_DETECT_DISTANCE_MM = 500


TURN_OPENING_DISTANCE_MM = 800


TURN_OPENING_CONFIRM_MS = 250


# ============================================================
# CAMERA
# ============================================================

IMAGE_WIDTH = 160

IMAGE_HEIGHT = 120


BLOB_ROI = (
    0,
    20,
    160,
    100
)


BLOB_MIN_PIXELS = 100

BLOB_MIN_AREA = 100


# ============================================================
# COLOUR THRESHOLDS
#
# IMPORTANT:
#
# Calibrate these using OpenMV Threshold Editor.
#
# These are placeholders only.
#
# WRO specifies:
#
# Red pillar:
# RGB 238,39,55
#
# Green pillar:
# RGB 68,214,44
#
# Parking marker:
# RGB 255,0,255
#
# OpenMV uses LAB thresholds so you MUST calibrate these
# under your competition lighting.
# ============================================================


RED_THRESHOLDS = [
    (24, 76, 21, 127, 51, 8)
]


#GREEN_THRESHOLDS = [(14, 25, -128, -4, 11, 42)]
GREEN_THRESHOLDS = [(17, 100, -128, -19, -128, 52)]

MAGENTA_THRESHOLDS = [
    (20, 81, 28, 98, -128, 31)
]


# ============================================================
# TRAFFIC SIGN DIMENSIONS
#
# Official pillar width is 50 mm.
# ============================================================

TRAFFIC_SIGN_WIDTH_MM = 50


# Desired horizontal clearance from pillar

DESIRED_CLEARANCE_MM = 120


MIN_OFFSET_PX = 18

MAX_OFFSET_PX = 55


# ============================================================
# PASSING CONDITIONS
# ============================================================

PASS_BLOB_PIXELS = 1500


PASS_ERROR_TOLERANCE_PX = 7


PASS_CONFIRM_FRAMES = 3


BLOB_CLEAR_FRAMES = 4

# Blob-loss confirmation. A near blob is only treated as passed if it
# disappeared near an image edge for several consecutive frames.
BLOB_LOST_CONFIRM_FRAMES = 3
BLOB_PASS_EDGE_MARGIN_PX = 15
BLOB_ABORT_MISSING_FRAMES = 6


# ============================================================
# BLOB PID
# ============================================================

BLOB_KP = 0.4

BLOB_KI = 0

BLOB_KD = 0


NEAR_BLOB_PIXELS = 900


NEAR_D_MULTIPLIER = 2.0


FAR_ERROR_CLAMP = 55

NEAR_ERROR_CLAMP = 28


# Change to -1 if steering is reversed

BLOB_STEERING_SIGN = -1


# Amount of IMU heading correction mixed
# into obstacle guidance

IMU_BLOB_CORRECTION = 0.15


# ============================================================
# IMU PID
# ============================================================

IMU_KP = 0.3

IMU_KI = 0

IMU_KD = 0


# Change to -1 if necessary

IMU_STEERING_SIGN = 1


# ============================================================
# 90 DEGREE TURN
# ============================================================

TURN_TOLERANCE_DEG = 3


TURN_CONFIRM_FRAMES = 4


# Assumes positive yaw = CCW

CW_TURN_CHANGE = -90

CCW_TURN_CHANGE = 90


# ============================================================
# PARKING
# ============================================================

# IMPORTANT:
#
# Enter your actual robot length.
#
# Official parking-space length:
#
# 1.5 x robot length
#

ROBOT_LENGTH_MM = 100


PARKING_SPACE_LENGTH_MM = (
    1.5
    *
    ROBOT_LENGTH_MM
)


# Official parking-space width = 200 mm

PARKING_SPACE_WIDTH_MM = 200


# Desired distance to outer wall

PARK_WALL_DISTANCE_MM = 120


PARK_DISTANCE_TOLERANCE_MM = 15


PARK_HEADING_TOLERANCE_DEG = 3


PARK_CONFIRM_FRAMES = 5


# Magenta marker size required to begin parking

MAGENTA_TRIGGER_PIXELS = 700

# Require both magenta parking markers before starting the parking sequence.
MAGENTA_SECONDARY_TRIGGER_PIXELS = 250
MAGENTA_CONFIRM_FRAMES = 2


# Parking manoeuvre distances.
#
# These must be calibrated on your actual vehicle.


PARK_FORWARD_ALIGN_MM = 120


PARK_REVERSE_FIRST_MM = 150


PARK_REVERSE_SECOND_MM = 170


PARK_FINAL_MIN_DISTANCE_MM = 80

# Prevent endless reverse travel during final alignment. Tune on the real car.
PARK_FINAL_MAX_DISTANCE_MM = 180

# Steering/yaw response reverses while driving backwards on an Ackermann car.
PARK_REVERSE_STEERING_SIGN = -1


# Parking steering angles

PARK_LEFT_IN = STEERING_LEFT

PARK_LEFT_COUNTER = STEERING_RIGHT


PARK_RIGHT_IN = STEERING_RIGHT

PARK_RIGHT_COUNTER = STEERING_LEFT


# ============================================================
# GLOBAL CONTROL VARIABLES
# ============================================================

control_buf = b""


control_encoder = 0

control_tof0 = 0

control_tof1 = 0


left_tof = 0

right_tof = 0


current_yaw = 0


course_direction = None


robot_state = "WAIT_FOR_START"


state_start_time = 0

state_start_encoder = 0


round_start_time = None


straight_heading = 0

turn_target = 0


lap_count = 0

turns_this_lap = 0


waiting_for_lap_confirmation = False

lap_corner_encoder = 0


parking_enabled = False


opening_start_time = None


blob_pass_count = 0

blob_missing_count = 0

last_blob_size = 0
last_blob_cx = None


resume_state_after_blob = (
    "NORMAL_DRIVING"
)


current_sign_colour = None


turn_confirm_count = 0


imu_counter_control = 0

imu_tared_control = False


parking_side = None

parking_heading = 0

parking_confirm_count = 0


magenta_detect_count = 0

# Saved start encoder when a parking stage is interrupted by obstacle avoidance.
parking_resume_encoder_start = None


# ============================================================
# START BUTTON
#
# Uses OpenMV built-in user button.
#
# This does NOT change any of your external pin assignments.
# ============================================================

try:

    from pyb import Switch

    start_switch = Switch()

except:

    start_switch = None


# For bench testing only.
#
# Competition:
# KEEP FALSE

ALLOW_AUTOSTART_FOR_TESTING = True

if start_switch is None and not ALLOW_AUTOSTART_FOR_TESTING:
    print("WARNING: pyb.Switch() is unavailable. Competition start will not work until the built-in start button API is confirmed.")


def start_button_pressed():

    if (
        ALLOW_AUTOSTART_FOR_TESTING
    ):

        return True


    if start_switch is None:

        return False


    try:

        return start_switch()

    except:

        return False


# ============================================================
# SAFE UART READER
#
# Original read_UART() remains unchanged.
# ============================================================

control_pattern = re.compile(
    r'encoder count:\s*(-?\d+),\s*'
    r'tof0:\s*(\d+),\s*'
    r'tof1:\s*(\d+)'
)


def read_control_UART():



    global control_buf

    global control_encoder

    global control_tof0

    global control_tof1

    global left_tof

    global right_tof


    if uart.any() > 0:

        incoming = uart.read(
            uart.any()
        )


        if incoming:

            control_buf += incoming


    while b'\n' in control_buf:

        line_byte, control_buf = (
            control_buf.split(
                b'\n',
                1
            )
        )


        try:

            line_string = (
                line_byte
                .decode('utf-8')
                .strip()
            )

        except:

            continue


        match = (
            control_pattern.search(
                line_string
            )
        )


        if match:

            control_encoder = int(
                match.group(1)
            )


            control_tof0 = int(
                match.group(2)
            )


            control_tof1 = int(
                match.group(3)
            )


            if TOF0_IS_LEFT:

                left_tof = (
                    control_tof0
                )

                right_tof = (
                    control_tof1
                )


            else:

                left_tof = (
                    control_tof1
                )

                right_tof = (
                    control_tof0
                )


# ============================================================
# SAFE IMU READER
#
# Original read_IMU() remains unchanged.
# ============================================================

def read_control_IMU():

    global current_yaw

    global imu_counter_control

    global imu_tared_control


    try:

        R, T, P = bno.euler


        # Your original code displays:
        #
        # R = X
        # T = Y
        # P = Z
        #
        # Use Z as yaw.

        current_yaw = P


        imu_counter_control += 1


        if (
            imu_counter_control == 10
            and
            not imu_tared_control
        ):

            try:

                bno.tare()

            except:

                print('imu tare fail')


            imu_tared_control = True


            print(
                "IMU TARED"
            )


    except Exception as error:

        print(
            "IMU ERROR:",
            error
        )


# ============================================================
# MOTOR STOP
# ============================================================

def robot_stop():

    speed.duty_u16(0)


# ============================================================
# ENCODER DISTANCE
# ============================================================

def encoder_distance_mm(
    difference
):

    revolutions = (
        abs(difference)
        /
        ENCODER_COUNTS_PER_REV
    )


    return (
        revolutions
        *
        WHEEL_CIRCUMFERENCE_MM
    )


# ============================================================
# ANGLE WRAPPING
# ============================================================

def wrap_angle(angle):

    while angle > 180:

        angle -= 360


    while angle < -180:

        angle += 360


    return angle


# ============================================================
# CAMERA INITIALISATION
# ============================================================

sensor.reset()


sensor.set_pixformat(
    sensor.RGB565
)


sensor.set_framesize(
    sensor.QQVGA
)

sensor.set_vflip(True)
sensor.set_hmirror(True)

sensor.skip_frames(
    time=2000
)


sensor.set_auto_gain(
    False
)


sensor.set_auto_whitebal(
    False
)


print(
    "CAMERA READY"
)


# ============================================================
# PID CONTROLLER
# ============================================================

class PIDController:

    def __init__(
        self,
        kp,
        ki,
        kd
    ):

        self.kp = kp

        self.ki = ki

        self.kd = kd


        self.integral = 0

        self.previous_error = 0

        self.previous_time = None


    def reset(self):

        self.integral = 0

        self.previous_error = 0

        self.previous_time = None


    def calculate(
        self,
        error,
        d_multiplier=1.0
    ):

        now = ticks_ms()


        if self.previous_time is None:

            dt = 0.03


        else:

            dt = (
                ticks_diff(
                    now,
                    self.previous_time
                )
                /
                1000
            )


            if dt <= 0:

                dt = 0.001


        self.integral += (
            error
            *
            dt
        )


        derivative = (
            error
            -
            self.previous_error
        ) / dt


        output = (
            self.kp
            *
            error
            +
            self.ki
            *
            self.integral
            +
            self.kd
            *
            d_multiplier
            *
            derivative
        )


        self.previous_error = error

        self.previous_time = now


        return output


# ============================================================
# PID OBJECTS
# ============================================================

blob_PID = PIDController(
    BLOB_KP,
    BLOB_KI,
    BLOB_KD
)


imu_PID = PIDController(
    IMU_KP,
    IMU_KI,
    IMU_KD
)


parking_heading_PID = PIDController(
    1.0,
    0,
    0.12
)


parking_distance_PID = PIDController(
    0.08,
    0,
    0.02
)


# ============================================================
# CHANGE STATE
# ============================================================

def change_state(
    new_state
):

    global robot_state

    global state_start_time

    global state_start_encoder


    robot_state = new_state


    state_start_time = (
        ticks_ms()
    )


    state_start_encoder = (
        control_encoder
    )


    print(
        "STATE ->",
        new_state
    )


# ============================================================
# DETERMINE CW / CCW
#
# Wall LEFT  = CW
# Wall RIGHT = CCW
# ============================================================

def detect_course_direction():

    global course_direction


    print(
        "LEFT TOF:",
        left_tof,
        "RIGHT TOF:",
        right_tof
    )


    left_wall = 0 < left_tof <= WALL_DETECT_DISTANCE_MM
    right_wall = 0 < right_tof <= WALL_DETECT_DISTANCE_MM

    if left_wall and not right_wall:

        course_direction = "CW"
        print("CW TRACK")
        return True

    elif right_wall and not left_wall:

        course_direction = "CCW"
        print("CCW TRACK")
        return True

    elif left_wall and right_wall:

        if left_tof < right_tof:
            course_direction = "CW"
            print("CW TRACK")
        else:
            course_direction = "CCW"
            print("CCW TRACK")
        return True

    course_direction = None
    print("NO VALID STARTING WALL DETECTED")
    return False


# ============================================================
# CAMERA TRAFFIC-SIGN DETECTION
#
# Returns:
#
# blob
# colour
#
# Largest red/green blob is assumed closest.
# ============================================================

def detect_traffic_sign():

    img = sensor.snapshot()


    red_blobs = img.find_blobs(

        RED_THRESHOLDS,

        roi=BLOB_ROI,

        pixels_threshold=(
            BLOB_MIN_PIXELS
        ),

        area_threshold=(
            BLOB_MIN_AREA
        ),

        merge=True
    )


    green_blobs = img.find_blobs(

        GREEN_THRESHOLDS,

        roi=BLOB_ROI,

        pixels_threshold=(
            BLOB_MIN_PIXELS
        ),

        area_threshold=(
            BLOB_MIN_AREA
        ),

        merge=True
    )


    candidates = []


    for blob in red_blobs:

        candidates.append(
            (
                blob,
                "RED"
            )
        )


    for blob in green_blobs:

        candidates.append(
            (
                blob,
                "GREEN"
            )
        )


    if not candidates:

        return None, None


    closest = max(
        candidates,

        key=lambda item:

            item[0].pixels
    )


    blob = closest[0]

    colour = closest[1]


    img.draw_rectangle(
        blob.rect
    )


    img.draw_cross(
        (blob.cx,
        blob.cy)
    )


    return (
        blob,
        colour
    )


# ============================================================
# PARKING CAMERA
#
# Detect:
#
# RED/GREEN traffic signs
# MAGENTA parking markers
#
# in same frame.
# ============================================================

def parking_camera_detection():

    img = sensor.snapshot()


    candidates = []


    red_blobs = img.find_blobs(

        RED_THRESHOLDS,

        roi=BLOB_ROI,

        pixels_threshold=(
            BLOB_MIN_PIXELS
        ),

        area_threshold=(
            BLOB_MIN_AREA
        ),

        merge=True
    )


    green_blobs = img.find_blobs(

        GREEN_THRESHOLDS,

        roi=BLOB_ROI,

        pixels_threshold=(
            BLOB_MIN_PIXELS
        ),

        area_threshold=(
            BLOB_MIN_AREA
        ),

        merge=True
    )


    magenta_blobs = img.find_blobs(

        MAGENTA_THRESHOLDS,

        pixels_threshold=150,

        area_threshold=150,

        merge=False
    )


    for blob in red_blobs:

        candidates.append(
            (
                blob,
                "RED"
            )
        )


    for blob in green_blobs:

        candidates.append(
            (
                blob,
                "GREEN"
            )
        )


    traffic_blob = None

    traffic_colour = None


    if candidates:

        traffic_blob, traffic_colour = max(

            candidates,

            key=lambda item:
            item[0].pixels
        )


        img.draw_rectangle(
            traffic_blob.rect
        )


        img.draw_cross(
            traffic_blob.cx,
            traffic_blob.cy()
        )


    # Sort magenta markers left to right

    magenta_blobs = sorted(

        magenta_blobs,

        key=lambda b:
        b.cx()
    )


    for marker in magenta_blobs:

        img.draw_rectangle(
            marker.rect
        )


    return (
        traffic_blob,
        traffic_colour,
        magenta_blobs
    )


# ============================================================
# TRAFFIC SIGN TARGET
#
# OFFICIAL THREE LAPS:
#
# RED:
# vehicle passes RIGHT
# therefore RED blob stays LEFT in camera
#
# GREEN:
# vehicle passes LEFT
# therefore GREEN blob stays RIGHT in camera
#
# AFTER THREE LAPS:
# either side is permitted.
# ============================================================

def get_sign_target(
    blob,
    colour
):

    image_centre = (
        IMAGE_WIDTH
        //
        2
    )


    offset_pixels = (
        DESIRED_CLEARANCE_MM
        *
        blob.w
        /
        TRAFFIC_SIGN_WIDTH_MM
    )


    offset_pixels = max(

        MIN_OFFSET_PX,

        min(
            MAX_OFFSET_PX,
            offset_pixels
        )
    )


    # ========================================================
    # DURING OFFICIAL THREE LAPS
    # ========================================================

    if lap_count < TARGET_LAPS:


        if colour == "RED":

            target_x = (
                image_centre
                -
                offset_pixels
            )


        else:

            target_x = (
                image_centre
                +
                offset_pixels
            )


    # ========================================================
    # AFTER THREE LAPS
    #
    # Any side is allowed.
    #
    # Move away from whichever side the obstacle
    # currently occupies.
    # ========================================================

    else:


        if blob.cx < image_centre:

            target_x = (
                image_centre
                -
                offset_pixels
            )


        else:

            target_x = (
                image_centre
                +
                offset_pixels
            )


    return target_x


# ============================================================
# OBSTACLE / TRAFFIC SIGN PID
# ============================================================

def avoid_traffic_sign(
    blob,
    colour
):

    global blob_pass_count

    global last_blob_size
    global last_blob_cx


    target_x = get_sign_target(
        blob,
        colour
    )


    camera_error = (
        blob.cx
        -
        target_x
    )


    blob_size = (
        blob.pixels
    )


    last_blob_size = (
        blob_size
    )
    last_blob_cx = blob.cx


    imu_error = wrap_angle(

        straight_heading
        -
        current_yaw
    )


    error = (
        camera_error
        -
        IMU_BLOB_CORRECTION
        *
        imu_error
    )


    # Close obstacle:
    #
    # increase D
    # reduce error clamp

    if (
        blob_size
        >=
        NEAR_BLOB_PIXELS
    ):

        error_limit = (
            NEAR_ERROR_CLAMP
        )

        d_multiplier = (
            NEAR_D_MULTIPLIER
        )


    else:

        error_limit = (
            FAR_ERROR_CLAMP
        )

        d_multiplier = 1.0


    error = max(

        -error_limit,

        min(
            error_limit,
            error
        )
    )


    correction = (
        blob_PID.calculate(
            error,
            d_multiplier
        )
    )


    correction = max(

        -MAX_BLOB_STEERING,

        min(
            MAX_BLOB_STEERING,
            correction
        )
    )


    steering = (
        STEERING_CENTRE
        +
        BLOB_STEERING_SIGN
        *
        correction
    )
    print(
        "BLOB DEBUG",
        "colour =", colour,
        "cx =", blob.cx,
        "target =", target_x,
        "camera error =", camera_error,
        "PID correction =", correction,
        "servo =", steering
    )

    set_position(
        int(steering)
    )


    drive(
        FORWARD,
        AVOID_SPEED
    )


    print(
        colour,
        "cx:",
        blob.cx,
        "target:",
        target_x,
        "pixels:",
        blob_size
    )


    # Passing condition

    if (
        blob_size
        >=
        PASS_BLOB_PIXELS

        and

        abs(camera_error)
        <=
        PASS_ERROR_TOLERANCE_PX
    ):

        blob_pass_count += 1


    else:

        blob_pass_count = 0


    return (
        blob_pass_count
        >=
        PASS_CONFIRM_FRAMES
    )


# ============================================================
# START OBSTACLE AVOIDANCE
# ============================================================

def begin_obstacle_avoidance(
    return_state,
    colour
):

    global blob_pass_count

    global blob_missing_count

    global resume_state_after_blob

    global current_sign_colour
    global parking_resume_encoder_start


    parking_states = (
        "PARK_FORWARD_POSITION",
        "PARK_REVERSE_IN",
        "PARK_COUNTERSTEER",
        "PARK_FINAL_ALIGN"
    )

    if return_state in parking_states:
        parking_resume_encoder_start = state_start_encoder
    else:
        parking_resume_encoder_start = None

    blob_pass_count = 0

    blob_missing_count = 0


    resume_state_after_blob = (
        return_state
    )


    current_sign_colour = colour


    blob_PID.reset()


    change_state(
        "OBSTACLE_AVOID"
    )


# ============================================================
# IMU STRAIGHT / TURN CONTROL
# ============================================================

def drive_with_IMU(
    target_heading,
    drive_speed,
    direction=FORWARD
):

    error = wrap_angle(

        target_heading
        -
        current_yaw
    )


    correction = (
        imu_PID.calculate(
            error
        )
    )


    correction = max(

        -MAX_IMU_STEERING,

        min(
            MAX_IMU_STEERING,
            correction
        )
    )


    steering = (
        STEERING_CENTRE
        +
        IMU_STEERING_SIGN
        *
        correction
    )


    set_position(
        int(steering)
    )


    drive(
        direction,
        drive_speed
    )


    return error


# ============================================================
# TURN OPENING DETECTION
# ============================================================

def turn_opening_detected():

    global opening_start_time


    if course_direction == "CW":

        wall_distance = (
            left_tof
        )


    else:

        wall_distance = (
            right_tof
        )


    if (
        wall_distance > 0
        and
        wall_distance > TURN_OPENING_DISTANCE_MM
    ):


        if opening_start_time is None:

            opening_start_time = (
                ticks_ms()
            )


        if (
            ticks_diff(
                ticks_ms(),
                opening_start_time
            )
            >=
            TURN_OPENING_CONFIRM_MS
        ):

            opening_start_time = None

            return True


    else:

        opening_start_time = None


    return False


# ============================================================
# START 90 DEGREE TURN
# ============================================================

def begin_90_turn():

    global turn_target


    if course_direction == "CW":

        turn_target = wrap_angle(

            straight_heading
            +
            CW_TURN_CHANGE
        )


    else:

        turn_target = wrap_angle(

            straight_heading
            +
            CCW_TURN_CHANGE
        )


    imu_PID.reset()


    change_state(
        "TURN_90"
    )


# ============================================================
# PARKING SIDE
#
# USER REQUIREMENT:
#
# CW  -> parking LEFT
# CCW -> parking RIGHT
# ============================================================

def set_parking_side():

    global parking_side


    if course_direction == "CW":

        parking_side = "LEFT"


    else:

        parking_side = "RIGHT"


    print(
        "PARKING SIDE:",
        parking_side
    )


# ============================================================
# PARKING WALL DISTANCE
# ============================================================

def parking_wall_distance():

    if parking_side == "LEFT":

        return left_tof


    return right_tof


# ============================================================
# START PARKING
# ============================================================

def begin_parallel_parking():

    global parking_heading

    global parking_confirm_count


    robot_stop()


    set_parking_side()


    parking_heading = (
        straight_heading
    )


    parking_confirm_count = 0


    parking_heading_PID.reset()

    parking_distance_PID.reset()


    change_state(
        "PARK_FORWARD_POSITION"
    )


# ============================================================
# FINAL PARKING ALIGNMENT
#
# Uses:
#
# IMU = parallel heading
# TOF = outer wall distance
# ============================================================

def final_parking_control():

    global parking_confirm_count


    wall_distance = (
        parking_wall_distance()
    )


    distance_error = (
        wall_distance
        -
        PARK_WALL_DISTANCE_MM
    )


    heading_error = wrap_angle(

        parking_heading
        -
        current_yaw
    )


    heading_correction = (
        parking_heading_PID.calculate(
            heading_error
        )
    )


    distance_correction = (
        parking_distance_PID.calculate(
            distance_error
        )
    )


    heading_correction = max(

        -25,

        min(
            25,
            heading_correction
        )
    )


    distance_correction = max(

        -15,

        min(
            15,
            distance_correction
        )
    )


    # Wall steering sign depends on side

    if parking_side == "LEFT":

        wall_correction = (
            -distance_correction
        )


    else:

        wall_correction = (
            distance_correction
        )


    correction = (
        heading_correction
        +
        wall_correction
    )

    correction *= PARK_REVERSE_STEERING_SIGN


    correction = max(

        -30,

        min(
            30,
            correction
        )
    )


    set_position(

        int(
            STEERING_CENTRE
            +
            correction
        )
    )


    # Final slow reverse adjustment

    drive(
        REVERSE,
        PARKING_SPEED
    )


    print(
        "PARK FINAL",
        "wall:",
        wall_distance,
        "heading:",
        heading_error
    )


    if (
        abs(distance_error)
        <=
        PARK_DISTANCE_TOLERANCE_MM

        and

        abs(heading_error)
        <=
        PARK_HEADING_TOLERANCE_DEG
    ):

        parking_confirm_count += 1


    else:

        parking_confirm_count = 0


    return (
        parking_confirm_count
        >=
        PARK_CONFIRM_FRAMES
    )


# ============================================================
# MAIN LOOP
# ============================================================

print(
    "WAITING FOR START BUTTON"
)


while True:


    # ========================================================
    # ALWAYS UPDATE UART + IMU
    # ========================================================

    read_control_UART()

    read_control_IMU()


    # ========================================================
    # ROUND TIME LIMIT
    # ========================================================

    if (
        round_start_time is not None
        and
        robot_state
        not in (
            "PARKED",
            "TIMEOUT"
        )
    ):

        elapsed_round_time = (
            ticks_diff(
                ticks_ms(),
                round_start_time
            )
        )


        if (
            elapsed_round_time
            >=
            ROUND_TIME_LIMIT_MS
        ):

            robot_stop()

            change_state(
                "TIMEOUT"
            )


    # ========================================================
    # LAP COMPLETION CONFIRMATION
    #
    # 4 turns alone do not instantly count the lap.
    #
    # Vehicle must travel out of the final corner.
    # ========================================================

    if (
        waiting_for_lap_confirmation
        and
        lap_count < TARGET_LAPS
        and
        robot_state == "NORMAL_DRIVING"
    ):

        distance_after_corner = (
            encoder_distance_mm(

                control_encoder
                -
                lap_corner_encoder
            )
        )


        if (
            distance_after_corner
            >=
            LAP_CONFIRM_DISTANCE_MM
        ):

            lap_count += 1


            turns_this_lap = 0


            waiting_for_lap_confirmation = (
                False
            )


            print(
                "===================="
            )

            print(
                "LAP",
                lap_count,
                "COMPLETE"
            )

            print(
                "===================="
            )


            if (
                lap_count
                >=
                TARGET_LAPS
            ):

                parking_enabled = True


                print(
                    "THREE LAPS COMPLETE"
                )

                print(
                    "PARKING ENABLED"
                )


    # ========================================================
    # WAIT FOR COMPETITION START BUTTON
    # ========================================================

    if robot_state == "WAIT_FOR_START":
        straight_heading = current_yaw

        imu_PID.reset()
        blob_PID.reset()

        change_state("LEAVE_STRAIGHT")
        '''robot_stop()
VV

        set_position(
            STEERING_CENTRE
        )
        #print( control_tof0, control_tof1)

        if (
            imu_tared_control

            and

            control_tof0 > 0

            and

            control_tof1 > 0

            and

            start_button_pressed()
        ):

            round_start_time = (
                ticks_ms()
            )


            if detect_course_direction():

                change_state(

                    "LEAVE_BACKUP"
                )

            else:

                round_start_time = None'''


    # ========================================================
    # LEAVING PARKING LOT
    #
    # BACK UP
    # ========================================================

    elif robot_state == "LEAVE_BACKUP":
        #print('leaving backup')
        set_position(
            STEERING_CENTRE
        )


        drive(1,LEAVING_SPEED)
        #print('reversing')

        distance = (
            encoder_distance_mm(

                control_encoder
                -
                state_start_encoder
            )
        )

        #print(distance)
        if (
            distance
            >=
            BACKUP_DISTANCE_MM
        ):

            robot_stop()
            sleep_ms(100)

            change_state(
                "LEAVE_RIGHT"
            )


    # ========================================================
    # HARDCODED RIGHT TURN
    # ========================================================

    elif robot_state == "LEAVE_RIGHT":

        set_position(
            STEERING_RIGHT
        )


        drive(
            FORWARD,
            LEAVING_SPEED
        )


        if (
            ticks_diff(ticks_ms(),state_start_time)>=RIGHT_TURN_TIME_MS):

            change_state(
                "LEAVE_STRAIGHT"
            )


    # ========================================================
    # STRAIGHT TO CLEAR PARKING WALL
    # ========================================================

    elif robot_state == "LEAVE_STRAIGHT":

        set_position(
            STEERING_CENTRE
        )


        drive(
            FORWARD,
            LEAVING_SPEED
        )


        if (
            ticks_diff(
                ticks_ms(),
                state_start_time
            )
            >=
            STRAIGHT_CLEAR_TIME_MS
        ):


            # CW:
            #
            # wall left
            # extra left turn

            if (
                course_direction
                ==
                "CW"
            ):

                change_state(
                    "LEAVE_LEFT"
                )


            # CCW:
            #
            # directly enter track

            else:

                straight_heading = (
                    current_yaw
                )


                imu_PID.reset()


                change_state(
                    "NORMAL_DRIVING"
                )


    # ========================================================
    # CW ONLY:
    # HARDCODED LEFT TURN
    # ========================================================

    elif robot_state == "LEAVE_LEFT":

        set_position(
            STEERING_LEFT
        )


        drive(
            FORWARD,
            LEAVING_SPEED
        )


        if (
            ticks_diff(
                ticks_ms(),
                state_start_time
            )
            >=
            LEFT_TURN_TIME_MS
        ):

            straight_heading = (
                current_yaw
            )


            imu_PID.reset()


            change_state(
                "NORMAL_DRIVING"
            )


    # ========================================================
    # NORMAL OFFICIAL-LAP DRIVING
    #
    # PRIORITY:
    #
    # 1. RED/GREEN pillar
    # 2. Corner
    # 3. Straight IMU
    # ========================================================

    elif robot_state == "NORMAL_DRIVING":


        # After 3 laps immediately start
        # searching for parking.

        if parking_enabled:

            change_state(
                "LOOK_FOR_PARKING"
            )


        else:

            blob, colour = (
                detect_traffic_sign()
            )


            # =================================================
            # TRAFFIC SIGN
            # =================================================

            if blob is not None:

                begin_obstacle_avoidance(
                    "NORMAL_DRIVING",
                    colour
                )


            # =================================================
            # TURN
            # =================================================

            elif turn_opening_detected():

                begin_90_turn()


            # =================================================
            # STRAIGHT
            # =================================================

            else:

                drive_with_IMU(
                    straight_heading,
                    NORMAL_SPEED
                )


    # ========================================================
    # OBSTACLE / TRAFFIC-SIGN AVOIDANCE
    # ========================================================

    elif robot_state == "OBSTACLE_AVOID":


        # During parking search use the
        # parking camera detector.

        if (
            resume_state_after_blob
            in (
                "LOOK_FOR_PARKING",
                "PARK_FORWARD_POSITION",
                "PARK_REVERSE_IN",
                "PARK_COUNTERSTEER",
                "PARK_FINAL_ALIGN"
            )
        ):

            blob, colour, markers = (
                parking_camera_detection()
            )


        else:

            blob, colour = (
                detect_traffic_sign()
            )


        if blob is not None:

            blob_missing_count = 0


            passed = (
                avoid_traffic_sign(
                    blob,
                    colour
                )
            )


            if passed:

                imu_PID.reset()


                blob_missing_count = 0


                change_state(
                    "PASS_OBSTACLE"
                )


        else:

            blob_missing_count += 1

            blob_was_near_edge = (
                last_blob_cx is not None
                and
                (
                    last_blob_cx <= BLOB_PASS_EDGE_MARGIN_PX
                    or
                    last_blob_cx >= IMAGE_WIDTH - BLOB_PASS_EDGE_MARGIN_PX
                )
            )

            if (
                last_blob_size >= NEAR_BLOB_PIXELS
                and
                blob_was_near_edge
                and
                blob_missing_count >= BLOB_LOST_CONFIRM_FRAMES
            ):

                imu_PID.reset()
                change_state("PASS_OBSTACLE")

            elif blob_missing_count >= BLOB_ABORT_MISSING_FRAMES:

                imu_PID.reset()
                change_state(resume_state_after_blob)


    # ========================================================
    # WAIT UNTIL TRAFFIC SIGN LEAVES CAMERA
    # ========================================================

    elif robot_state == "PASS_OBSTACLE":


        if (
            resume_state_after_blob
            in (
                "LOOK_FOR_PARKING",
                "PARK_FORWARD_POSITION",
                "PARK_REVERSE_IN",
                "PARK_COUNTERSTEER",
                "PARK_FINAL_ALIGN"
            )
        ):

            blob, colour, markers = (
                parking_camera_detection()
            )


        else:

            blob, colour = (
                detect_traffic_sign()
            )


        # Hold the correct heading while passing. If avoidance interrupted
        # a turn, continue toward the turn target instead of the old straight heading.
        if resume_state_after_blob == "TURN_90":
            pass_heading = turn_target
        else:
            pass_heading = straight_heading

        drive_with_IMU(
            pass_heading,
            AVOID_SPEED
        )


        if blob is None:

            blob_missing_count += 1


        else:

            blob_missing_count = 0


        if (
            blob_missing_count
            >=
            BLOB_CLEAR_FRAMES
        ):

            blob_PID.reset()

            imu_PID.reset()


            change_state(
                resume_state_after_blob
            )

            if (
                parking_resume_encoder_start is not None
                and
                resume_state_after_blob in (
                    "PARK_FORWARD_POSITION",
                    "PARK_REVERSE_IN",
                    "PARK_COUNTERSTEER",
                    "PARK_FINAL_ALIGN"
                )
            ):
                state_start_encoder = parking_resume_encoder_start


    # ========================================================
    # 90 DEGREE TURN
    # ========================================================

    elif robot_state == "TURN_90":

        blob, colour = (
            detect_traffic_sign()
        )


        # Obstacle has priority

        if blob is not None:

            begin_obstacle_avoidance(
                "TURN_90",
                colour
            )


        else:

            turn_error = (
                drive_with_IMU(
                    turn_target,
                    TURN_SPEED
                )
            )


            if (
                abs(turn_error)
                <=
                TURN_TOLERANCE_DEG
            ):

                turn_confirm_count += 1


            else:

                turn_confirm_count = 0


            if (
                turn_confirm_count
                >=
                TURN_CONFIRM_FRAMES
            ):

                turn_confirm_count = 0


                straight_heading = (
                    turn_target
                )


                imu_PID.reset()


                # =============================================
                # COUNT SUCCESSFUL CORNER
                # =============================================

                turns_this_lap += 1


                print(
                    "TURN:",
                    turns_this_lap,
                    "/",
                    TURNS_PER_LAP
                )


                if (
                    turns_this_lap
                    >=
                    TURNS_PER_LAP
                ):

                    waiting_for_lap_confirmation = (
                        True
                    )


                    lap_corner_encoder = (
                        control_encoder
                    )


                change_state(
                    "NORMAL_DRIVING"
                )


    # ========================================================
    # AFTER THREE LAPS:
    # FIND MAGENTA PARKING LOT
    #
    # RED/GREEN pillars can now be passed on either side.
    #
    # They still have priority over parking.
    # ========================================================

    elif robot_state == "LOOK_FOR_PARKING":

        blob, colour, markers = (
            parking_camera_detection()
        )


        # =====================================================
        # PRIORITY 1:
        # RED/GREEN TRAFFIC SIGN
        # =====================================================

        if blob is not None:

            begin_obstacle_avoidance(
                "LOOK_FOR_PARKING",
                colour
            )


        # =====================================================
        # PRIORITY 2:
        # MAGENTA PARKING MARKERS
        # =====================================================

        elif len(markers) >= 2:

            two_largest_markers = sorted(
                markers,
                key=lambda b: b.pixels,
                reverse=True
            )[:2]

            largest_marker = two_largest_markers[0]
            second_marker = two_largest_markers[1]

            if (
                largest_marker.pixels >= MAGENTA_TRIGGER_PIXELS
                and
                second_marker.pixels >= MAGENTA_SECONDARY_TRIGGER_PIXELS
            ):

                magenta_detect_count += 1

            else:

                magenta_detect_count = 0

            if magenta_detect_count >= MAGENTA_CONFIRM_FRAMES:

                robot_stop()
                begin_parallel_parking()


        # =====================================================
        # KEEP MOVING UNTIL PARKING LOT FOUND
        # =====================================================

        else:

            magenta_detect_count = 0

            drive_with_IMU(
                straight_heading,
                NORMAL_SPEED
            )


    # ========================================================
    # PARALLEL PARKING
    #
    # STAGE 1:
    #
    # Move slightly forward so the vehicle is positioned
    # beside / beyond the parking entrance.
    #
    # RED/GREEN obstacle ALWAYS has priority.
    # ========================================================

    elif robot_state == "PARK_FORWARD_POSITION":

        blob, colour, markers = (
            parking_camera_detection()
        )


        if blob is not None:

            begin_obstacle_avoidance(
                "PARK_FORWARD_POSITION",
                colour
            )


        else:

            set_position(
                STEERING_CENTRE
            )


            drive(
                FORWARD,
                PARKING_SPEED
            )


            distance = (
                encoder_distance_mm(

                    control_encoder
                    -
                    state_start_encoder
                )
            )


            if (
                distance
                >=
                PARK_FORWARD_ALIGN_MM
            ):

                robot_stop()


                change_state(
                    "PARK_REVERSE_IN"
                )


    # ========================================================
    # PARKING STAGE 2:
    #
    # Reverse toward parking side.
    #
    # CW  -> LEFT
    # CCW -> RIGHT
    # ========================================================

    elif robot_state == "PARK_REVERSE_IN":

        blob, colour, markers = (
            parking_camera_detection()
        )


        if blob is not None:

            begin_obstacle_avoidance(
                "PARK_REVERSE_IN",
                colour
            )


        else:


            if parking_side == "LEFT":

                set_position(
                    PARK_LEFT_IN
                )


            else:

                set_position(
                    PARK_RIGHT_IN
                )


            drive(
                REVERSE,
                PARKING_SPEED
            )


            distance = (
                encoder_distance_mm(

                    control_encoder
                    -
                    state_start_encoder
                )
            )


            if (
                distance
                >=
                PARK_REVERSE_FIRST_MM
            ):

                robot_stop()


                change_state(
                    "PARK_COUNTERSTEER"
                )


    # ========================================================
    # PARKING STAGE 3:
    #
    # Counter-steer to become parallel.
    # ========================================================

    elif robot_state == "PARK_COUNTERSTEER":

        blob, colour, markers = (
            parking_camera_detection()
        )


        if blob is not None:

            begin_obstacle_avoidance(
                "PARK_COUNTERSTEER",
                colour
            )


        else:


            if parking_side == "LEFT":

                set_position(
                    PARK_LEFT_COUNTER
                )


            else:

                set_position(
                    PARK_RIGHT_COUNTER
                )


            drive(
                REVERSE,
                PARKING_SPEED
            )


            distance = (
                encoder_distance_mm(

                    control_encoder
                    -
                    state_start_encoder
                )
            )


            heading_error = wrap_angle(

                parking_heading
                -
                current_yaw
            )


            # Either calibrated distance is reached
            # or vehicle has already become nearly parallel.

            if (
                distance
                >=
                PARK_REVERSE_SECOND_MM

                or

                (
                    distance
                    >=
                    PARK_REVERSE_SECOND_MM
                    * 0.6

                    and

                    abs(heading_error)
                    <=
                    6
                )
            ):

                robot_stop()


                parking_heading_PID.reset()

                parking_distance_PID.reset()


                change_state(
                    "PARK_FINAL_ALIGN"
                )


    # ========================================================
    # PARKING STAGE 4:
    #
    # Final fine alignment.
    #
    # IMU:
    # parallel to outside wall
    #
    # TOF:
    # correct distance to outside wall
    #
    # RED/GREEN still have absolute priority.
    # ========================================================

    elif robot_state == "PARK_FINAL_ALIGN":

        blob, colour, markers = (
            parking_camera_detection()
        )


        if blob is not None:

            begin_obstacle_avoidance(
                "PARK_FINAL_ALIGN",
                colour
            )


        else:

            final_distance = (
                encoder_distance_mm(

                    control_encoder
                    -
                    state_start_encoder
                )
            )


            parked_correctly = (
                final_parking_control()
            )


            if (
                parked_correctly
                and
                final_distance >= PARK_FINAL_MIN_DISTANCE_MM
                and
                final_distance <= PARK_FINAL_MAX_DISTANCE_MM
            ):

                robot_stop()


                set_position(
                    STEERING_CENTRE
                )


                print(
                    "========================"
                )

                print(
                    "PARKING COMPLETE"
                )

                print(
                    "========================"
                )


                change_state(
                    "PARKED"
                )

            elif final_distance > PARK_FINAL_MAX_DISTANCE_MM:

                robot_stop()
                set_position(STEERING_CENTRE)
                print("PARKING ALIGNMENT LIMIT REACHED - STOPPED FOR SAFETY")
                change_state("PARKED")


    # ========================================================
    # PARKED
    # ========================================================

    elif robot_state == "PARKED":

        robot_stop()


        set_position(
            STEERING_CENTRE
        )


    # ========================================================
    # THREE-MINUTE TIMEOUT
    # ========================================================

    elif robot_state == "TIMEOUT":

        robot_stop()


        set_position(
            STEERING_CENTRE
        )


    sleep_ms(20)
