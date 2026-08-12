from machine import UART

uart = UART(1, 115200)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1) #sets additional settings
buf = b"" # create empty byte object and assigns it to variable 'buf' (short for buffer)

while True:
    if uart.any() > 0: #if UART recieves any data:
        buf += uart.read(uart.any())  # grab everything currently waiting
        if b'\n' in buf: #if byte containing \n (newline indicator) is in the buffer:
            line, buf = buf.split(b'\n', 1)  # split off the first complete line
            print(line)









