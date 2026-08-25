from machine import UART
import re

uart = UART(1, 115200)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1) #sets additional settings
buf = b"" # create empty byte object and assigns it to variable 'buf' (short for buffer)
pattern = re.compile(r'encoder count:\s*(\d+),\s*tof0:\s*(\d+),\s*tof1:\s*(\d+)') #for UART parsing

#define variables below
encoder_count = 0
wheel_revolutions = 0
tof0 = 0
tof1 = 0

while True:
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
                wheel_rotations = encoder_count / (28*3) #divide by 28, since 7PPR encoder has 28 counts per rev. divide by 3, since gear ratio is 1:3
            print(f"Parsed -> Encoder: {encoder_count}, TOF0: {tof0}, TOF1: {tof1}")
        else:
            print("Failed to parse string structure")

# EXAMPLE OF line_byte when printed ---- b'encoder count: 1250, tof0: 3400, tof1: 42\r'
# EXAMPLE OF line_string ---- 'encoder count: 1250, tof0: 3400, tof1: 42'
