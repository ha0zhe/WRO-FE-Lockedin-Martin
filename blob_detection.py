import csi

# Setup camera.
csi0 = csi.CSI()
csi0.reset()
csi0.pixformat(csi.RGB565)
csi0.framesize(csi.QVGA)
sw = csi0.width()
sh = csi0.height()
csi.window(sw, 0.5*sh) #leave width as is, crop height to 50% (check irl)
csi0.snapshot(time=2000)  # skip csi0.snapshot for 2000ms for sensor to stabilise

red_thresholds = (30, 100, 15, 127, 15, 127)  # exmaple LAB threshold for red
green_thresholds = (,,,,,)
blue_thresholds = (,,,,,)
orange_thresholds = (,,,,,)
pink_thresholds = (,,,,,)

roi0 =(0, sh//2, sw, sh//2) # x,y,w,here refers to the frame size, NOT the blob size #example: take bottom half of frame
roi1 =(,,,)
x_stride =
y_stride =
area_threshold = 
# Take pictures.
while(True):
    csi0.snapshot()
    blobs = img.find_blobs([red_thresholds, green_thresholds] roi, x_stride, y_stride, area_threshold, merge = true )
    for b in blobs:
        img.draw_rectangle(b.rect, color=(255, 0, 0))
        img.draw_cross(b.cx, b.cy, color=(255, 0, 0))
        blob_centroid_x = b.cx()
        blob_centroid_y = b.cy()
        blob_width = b.w()
        blob_height = b.h()
        blob_rotation = b.rotation()
        