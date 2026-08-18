
import csi
import time

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
roi_line = (0, 0, cw, ch//2)   # ROI for line detection (check irl)

red_t = (0, 100, -23, 31, -32, 60)  # exmaple LAB threshold for red
green_t = (0, 0, 0, 0, 0, 0)
blue_t = (1, 0, 0, 0, 0, 0)
orange_t = (2, 0, 0, 0, 0, 0)
magenta_t = (3, 0, 0, 0, 0, 0)


img = csi0.snapshot()  # call once at the start of every control loop


def find_red():
    red_blobs = img.find_blobs([red_t], x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
    if red_blobs:
        b = red_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        red_cx = b.cx
        red_cy = b.cy
        red_w = b.w
        red_h = b.h
        red_rot = b.rotation
        print(red_cx, red_cy, red_w, red_h, red_rot)
    return b


def find_green():
    green_blobs = img.find_blobs([green_t], x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
    if green_blobs:
        b = green_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        green_cx = b.cx
        green_cy = b.cy
        green_w = b.w
        green_h = b.h
        green_rot = b.rotation
        print(green_cx, green_cy, green_w, green_h, green_rot)
    return b


def find_blue():
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
    orange_blobs = img.find_blobs([orange_t], roi=roi_line, x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
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


def find_magenta():
    magenta_blobs = img.find_blobs([magenta_t], roi=roi_line, x_stride=4, y_stride=4, area_threshold=200, merge=True, max_blobs=1)
    if magenta_blobs:
        b = magenta_blobs[0]
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        magenta_cx = b.cx
        magenta_cy = b.cy
        magenta_w = b.w
        magenta_h = b.h
        magenta_rot = b.rotation
        print(magenta_cx, magenta_cy, magenta_w, magenta_h, magenta_rot)
    return b
