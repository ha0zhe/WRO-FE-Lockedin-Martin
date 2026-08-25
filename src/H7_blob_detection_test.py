
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

red_t = (0, 100, -23, 31, -32, 60)  # exmaple LAB threshold for red. ...00001, 1


# Take pictures.
while (True):
    clock.tick()
    # print(clock.fps())
    img = csi0.snapshot()
    blobs = img.find_blobs([red_t], x_stride=4, y_stride=4, area_threshold=200, merge=True)
    for b in blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross((b.cx, b.cy), color=(255, 0, 0))
        red_cx = b.cx
        red_cy = b.cx
        red_w = b.w
        red_h = b.h
        red_rot = b.rotation
        print(red_cx, red_cy, red_w, red_h, red_rot)
