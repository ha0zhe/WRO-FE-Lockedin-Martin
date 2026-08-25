# WRO-FE-Lockedin-Martin

# Team information:
Team ID: FE-XXX-01
Team name: Lockedin Martin
Team members:
- Yuan Hao Zhe
- Liu Xinji
- Om Joshi Vaibhav

# Overview
Welcome to the github repository of team Lockedin Martin for WRO 2026.

The Wro FE competition consists of 2 rounds: the open round and the obstacle round. in the open round, the vehicle must autonomously drive 3 laps on a track with no obstacles and stop at its starting position. in the obstacle round, the vehicle must navigate 3 laps on a track containing red and green traffic signs, turning right when encountering a red sign and left when encountering a green sign. For the obstacle round, the vehicle must also autonomously parallel-park in a parking lot that is demarcated by magenta blocks. 

All the information about the vehicle, including technical specifications, the design process and how it works, can be found in the engineering journal. The wiring diagram can be found in the schemes folder, the CAD models under the models folder, and the code in the src folder. 

Our team uses  dual microcontroller setup for this competition: the Openmv H7 plus for blob detection and navigation. and the RP2040 zero for sensor reading. code for specific functions of the H7, such as UART reading and blob detection, can be found in the files with names beginning with H7_ in the src folder. the RP2040 sensor reading code can be found in the same folder, compiled in one script.

# Build details
The chassis is printed at 0.20 mm nozzle diameter using PLA filament. The number of walls we used is 4 and the infill percentage is 15%. The infill pattern is grid.

Sandpaper may need to be used when assembling the chasis, if the fit is too tight.

The screws and nuts used to mount the steering mechanism must be snug, but not tight enough to hinder the actuation of the steering mechanism. 

The electronics are all connected using jumper cables without the need for soldering, with the exception of the power distribution board, which is direct soldered to the step down buck converters. More details can be found in the engineering journal. when soldering, keep the iron temperature at about 350 degrees and use liberal amounts of flux. be careful when holding the components with alligator clips as they might damage some delicate components on the board.

To charge the Lipo battery, a dedicated Lipo charger, such as the HOTA D6 Pro, must be used to avoid damaging the battery. do not discharge the battery below 3v and do not overcharge it over 4.2v

# Software details

Openmv IDE is used to run and debug the H7 code, while Arduino IDE is used for the RP2040. Thonny could also be used for the H7 if the camera is not needed e.g. when testing the UART.

Openmv IDE's threshold is used to tune the CIELAB color thresholds used in blob detection. As much as possible, refer to Openmv's excellent documentation and tutorials.

For the code to be saved on the H7, you must save it on the H7's internal memory as main.py. This can be done manually, through dragging and dropping files in file manager, or it can be done in the Openmv IDE in File --> save script under Openmv cam

To setup Thonny for Openmv H7 plus:
1. Install Thonny, then Run → Select interpreter.
2. Choose "MicroPython (generic)" from the interpreter dropdown (there's no dedicated OpenMV entry — generic is correct since it just      talks raw REPL over serial).
3. Pick the port your H7 Plus enumerates as (or leave on auto-detect if it's the only device attached).
4. Click OK — Thonny's shell should show the >>> REPL prompt, and the Files pane will let you browse/edit files directly on the camera's internal flash or SD card.

To setup Openmv Ide for Openmv H7 plus:
1. Download and install OpenMV IDE from openmv.io/pages/download — no separate board package needed, unlike Arduino.
2. Plug in the H7 Plus via USB, click Connect (bottom-left plug icon).
3. If prompted with a firmware update on first connect — accept it. It'll ask whether to erase the internal filesystem: say No if you      have scripts stored on internal flash you want to keep, otherwise Yes for a clean start. It flashes over DFU automatically (green       LED fades in/out during the process) and reconnects when done.
4. Open helloworld_1.py or your own script, hit the Play (bottom-left run) button — you'll get a live frame buffer view alongside           serial console output, which is what makes it good for tuning your blob-detection thresholds.

To setup Arduino Ide for RP2040 Zero:
1. Add the board package URL. Open Arduino IDE → File → Preferences → paste this into "Additional Boards Manager URLs":
   https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
   (If you already have another URL      there, e.g. for ESP32, separate them with a comma.)
3. Install the core. Tools → Board → Boards Manager → search "pico" → install "Raspberry Pi Pico/RP2040/RP2350" by Earle F. Philhower,     III. This is the community core (not the official Arduino-Mbed one) — it's the one with full RP2040 peripheral support (PIO,            multicore, etc.) and is what you're already using per your Serial/Serial1/Serial2 debugging.
4. Select the board. Tools → Board → Raspberry Pi RP2040 Boards → Waveshare RP2040 Zero. If your installed core version doesn't list it    specifically, "Generic RP2040" also works fine for a Zero.
5. Upload. Hold BOOT, plug in via USB (or hold BOOT and tap RESET if already connected), release once the RPI-RP2 drive appears.           Arduino should now show a COM/tty port — select it and upload normally. After the first proper Arduino sketch is flashed, subsequent    uploads happen automatically over USB without needing BOOT mode again. If not, hold down the boot button, connect the RP2040, select
   and connect to the DFU port n the tools menu. After uploading the code, you should be able to connect via COM port in the same          tools menu
   
# Tips and tricks

1. Make sure all pin headers are tightly connected, especially for I2C. loose connections will degrade the high frequency clock signal and prevent it from working
2. Make sure to tighten all screws and nuts before testing. not doing so will result in inconsistent turn radii.
3. Make sure to wipe the TOF lens before testing it, to prevent oils from interfering with the reading
4. When tuning the color thresholds, use the narrowest thresholds that can still correctly identify the blocks under varying lighting conditions (e.g on different positions on the track)
5. do not touch the IMU while it is being tared.
