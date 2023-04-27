import colorsys
import cv2 as cv
import converter
title_window = 'Linear Blend'
nametrack = ['H', 'S', 'V']
hsv_min = [0,0,0]
hsv_max = [0,0,0]
pos = None
deltahsv = 0
size =[]
def callback():
    pass

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global pos
    global size
    if event == cv.EVENT_LBUTTONDOWN and len(size)>0:
        pos = [x,y]
    elif event == cv.EVENT_LBUTTONDOWN and len(size) == 0:
        size.append([x,y])
    elif event == cv.EVENT_LBUTTONDOWN and len(size) == 1:
        newpos = [x,y]
        currentpos = size[0]
        size = []
        size = [abs(newpos[0] - currentpos[0]), abs(newpos[1] - currentpos[1])]
def hsvMin1(val):
    global hsv_min
    hsv_min[0] = val
def deltahsvfunc(val):
    pass
def hsvMin2(val):
    global hsv_min
    hsv_min[1] = val
def hsvMin3(val):
    global hsv_min
    hsv_min[2] = val
def hsvMax1(val):
    global hsv_max
    hsv_max[0] = val
def hsvMax2(val):
    global hsv_max
    hsv_max[1] = val
def hsvMax3(val):
    global hsv_max
    hsv_max[2] = val
cv.namedWindow(title_window, cv.WINDOW_NORMAL)
cv.namedWindow("Detected")
cv.createTrackbar("H_min", title_window, 0, 255, hsvMin1)
cv.createTrackbar("S_min", title_window, 0, 255, hsvMin2)
cv.createTrackbar("V_min", title_window, 0, 255, hsvMin3)
cv.createTrackbar("H_max", title_window, 0, 255, hsvMax1)
cv.createTrackbar("S_max", title_window, 0, 255, hsvMax2)
cv.createTrackbar("V_max", title_window, 0, 255, hsvMax3)
cv.createTrackbar("deltahsv", title_window, 0, 255, deltahsvfunc)
cv.setMouseCallback("Detected", click_and_crop)
#cv.createTrackbar("Size_min", title_window, 0, 1920,callback)
#cv.createTrackbar("V_max", title_window, 0, 1920,callback)
cap = cv.VideoCapture(1)
while True:
    deltahsv = cv.getTrackbarPos("deltahsv", title_window)
    ret, work_hsv = cap.read()
    img = work_hsv
    if ret:
        work_hsv = cv.cvtColor(work_hsv, cv.COLOR_BGR2HSV)
        work_hsv = cv.blur(work_hsv,(30,30))
        only_hsv = cv.inRange(work_hsv, (hsv_min[0],hsv_min[1],hsv_min[2]), (hsv_max[0],hsv_max[1],hsv_max[2]))
        cv.imshow('only_hsv',only_hsv )

        cv.imshow("Detected",img )
    else:
        print("Error Drawing Frame")
    if pos != None:
        colorbgr = img[pos[1],pos[0]]
        print("rgb" , colorbgr)
        colorhsv = converter.rgb_to_hsv(colorbgr[2], colorbgr[1], colorbgr[0])
        print(colorhsv)
        for i in range(len(hsv_min)):
            if (colorhsv[i] - 10) < 0:
                hsv_min[i] = 0
            else:
                hsv_min[i] = int(colorhsv[i] - 10)
        for i in range(len(hsv_max)):
            if (colorhsv[i] + 10) > 255:
                hsv_max[i] = 255
            else:
                hsv_max[i] = int(colorhsv[i] + 10)
        cv.setTrackbarPos("H_min", title_window,hsv_min[0])
        cv.setTrackbarPos("S_min", title_window,hsv_min[1])
        cv.setTrackbarPos("V_min", title_window, hsv_min[2])
        cv.setTrackbarPos("H_max", title_window, hsv_max[0])
        cv.setTrackbarPos("S_max", title_window, hsv_max[1])
        cv.setTrackbarPos("V_max", title_window, hsv_max[2])
        pos = None
    if cv.waitKey(1) == ord("q"):
        break
cap.release()
# Destroy all the windows
cv.destroyAllWindows()
