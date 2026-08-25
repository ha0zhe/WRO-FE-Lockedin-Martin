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

All the information about the vehicle, including technical specifications, the design process and how it works, can be found in the engineering journal in the docs folder. The wiring diagram can be found in the schemes folder, the CAD models under the models folder, and the code in the src folder. 

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

# Tips and tricks
