
import cv2
globalcontours = []
def detected(image,x,y):
    global globalcontours
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, (3,3))
    ret, binary = cv2.threshold(gray, 128, 128,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    with_contours = cv2.drawContours(image, contours, -1,(255,0,255),3)
    if len(contours) > 0:
        cnt = contours[0]
        M = cv2.moments(cnt)
        globalcontours.append([int(M['m10']/M['m00']) + x, int(M['m01']/M['m00']) + y])
    flag = False
    if len(contours) >= 1:
            for contour in contours:
                if contour.shape[0] > 5:
                    flag = True
    return flag
def findobject(image):
    globalcontours = []
    slots = [[],[]]
    array = [[[74,0],[111,36]],[[119,0],[156,36]],[[164,0],[201,36]],[[75,96],[111,131]],[[119,96],[156,131]],[[164,96],[201,131]],[[74,139],[111,174]],[[119,139],[156,174]],[[164,139],[201,174]],[[74,239],[111,273]],[[119,239],[156,273]],[[164,239],[201,273]]]
    img = cv2.imread(image)
    img1 = img
    for i in range(len(array)):
        roi = img[array[i][0][1]:array[i][1][1], array[i][0][0]:array[i][1][0]] 
        if detected(roi, array[i][0][0], array[i][0][1]) == True:
            slots[1].append(i+1)
        elif detected(roi,array[i][0][0], array[i][0][1]) == False:
            slots[0].append(i+1)
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, (3,3))
    ret, binary = cv2.threshold(gray, 128, 128,cv2.THRESH_BINARY)
    for i in range(len(globalcontours)):     
        cv2.circle(binary,(globalcontours[i][0],globalcontours[i][1]), 1,(255,255,255), -1)
    width = int(275)
    height = int(275)
    dim = (width, height)
    cv2.imshow("With_contours_BINARY",cv2.resize(binary, dim))
    cv2.moveWindow("With_contours_BINARY", 10, 10)
    for i in range(len(globalcontours)):     
        cv2.circle(img,(globalcontours[i][0],globalcontours[i][1]), 15,(255,255,255), 2)
    width = int(275)
    height = int(275)
    dim = (width, height)
    cv2.imshow("with contours",cv2.resize(img, dim))
    cv2.moveWindow("with contours", 10, 290)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return slots
