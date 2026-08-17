
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
csi0.window([0, 0, sw, sh//2])  # leave width as is, crop height to 50% (check irl)
csi0.snapshot(time=2000)  # skip csi0.snapshot for 2000ms for sensor to stabilise

red_t = (0, 100, -23, 31, -32, 60)  # exmaple LAB threshold for red
green_t = (0, 0, 0, 0, 0, 0)
blue_t = (1, 0, 0, 0, 0, 0)
orange_t = (2, 0, 0, 0, 0, 0)
magenta_t = (3, 0, 0, 0, 0, 0)


def find_red():
    img = csi0.snapshot()
    red_blobs = img.find_blobs([red_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in red_blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        red_cx = b.cx
        red_cy = b.cx
        red_w = b.w
        red_h = b.h
        red_rot = b.rotation
        print(red_cx, red_cy, red_w, red_h, red_rot)


def find_green():
    img = csi0.snapshot()
    green_blobs = img.find_blobs([green_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in green_blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        green_cx = b.cx
        green_cy = b.cx
        green_w = b.w
        green_h = b.h
        green_rot = b.rotation
        print(green_cx, green_cy, green_w, green_h, green_rot)


# Blue implementation
def find_blue():
    img = csi0.snapshot()
    blue_blobs = img.find_blobs([blue_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in blue_blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        blue_cx = b.cx
        blue_cy = b.cy
        blue_w = b.w
        blue_h = b.h
        blue_rot = b.rotation
        print(blue_cx, blue_cy, blue_w, blue_h, blue_rot)


# Orange implementation
def find_orange():
    img = csi0.snapshot()
    orange_blobs = img.find_blobs([orange_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in orange_blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        orange_cx = b.cx
        orange_cy = b.cy
        orange_w = b.w
        orange_h = b.h
        orange_rot = b.rotation
        print(orange_cx, orange_cy, orange_w, orange_h, orange_rot)


def find_magenta():
    img = csi0.snapshot()
    magenta_blobs = img.find_blobs([magenta_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in magenta_blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        magenta_cx = b.cx
        magenta_cy = b.cy
        magenta_w = b.w
        magenta_h = b.h
        magenta_rot = b.rotation
        print(magenta_cx, magenta_cy, magenta_w, magenta_h, magenta_rot)
