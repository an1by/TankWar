import cv2 as cv
import random
array = [[[74,0],[111,36]],[[119,0],[156,36]],[[164,0],[201,36]],[[75,96],[111,131]],[[119,96],[156,131]],[[164,96],[201,131]],[[74,139],[111,174]],[[119,139],[156,174]],[[164,139],[201,174]],[[74,239],[111,273]],[[119,239],[156,273]],[[164,239],[201,273]]]
def place(count, pathcount):
	ar = []
	img = cv.imread('png\\data.png') 
	for i in range(int(count)):
		cnt = random.randint(1,12)
		if not(cnt in ar):
			ar.append(cnt)
			cv.circle(img,(array[cnt - 1][0][0] + (array[cnt - 1][1][0] - array[cnt - 1][0][0]) // 2,array[cnt - 1][0][1] + (array[cnt - 1][1][1] - array[cnt - 1][0][1]) // 2), 5,(255,255,255), -1) 
		else :
			while cnt in ar:
				cnt = random.randint(1,12)
			ar.append(cnt)
			cv.circle(img,(array[cnt - 1][0][0] + (array[cnt - 1][1][0] - array[cnt - 1][0][0]) // 2,array[cnt - 1][0][1] + (array[cnt - 1][1][1] - array[cnt - 1][0][1]) // 2), 5,(255,255,255), -1) 
	cv.imwrite('png\\data' + str(pathcount) +'.png', img)
	return 'png\\data' + str(pathcount) +'.png'
