from machine import PWM, Pin

servo = PWM(Pin("P7"), freq=50, duty_ns=1_500_000)  # centre

def set_position(angle):
    # angle: 0..180 degrees mapped to 1.0..2.0 ms
    pulse_us = 1000 + (angle * 1000) // 180
    servo.duty_ns(pulse_us * 1000)

set_position(25)	# full right
set_position(135)    # full left
set_position(80)     # centre
