import cv2 as cv
array = [[[74,0],[111,36]],[[119,0],[156,36]],[[164,0],[201,36]],[[75,96],[111,131]],[[119,96],[156,131]],[[164,96],[201,131]],[[74,139],[111,174]],[[119,139],[156,174]],[[164,139],[201,174]],[[74,239],[111,273]],[[119,239],[156,273]],[[164,239],[201,273]]]
def placepersonprog(array1 , pathcount):
        ar = []
        for i in range(len(array1)):
            for j in range(12):
                if array1[i][0] >= array[j][0][0] and array1[i][0] <= array[j][1][0] and array1[i][1] >= array[j][0][1] and array1[i][1] <= array[j][1][1]:
                        ar.append(j + 1)
        img = cv.imread('png\\data.png')
        for i in range(len(array1)):
                cnt = ar[i]
                if cnt in ar:
                        cv.circle(img,(array[cnt - 1][0][0] + (array[cnt - 1][1][0] - array[cnt - 1][0][0]) // 2,array[cnt - 1][0][1] + (array[cnt - 1][1][1] - array[cnt - 1][0][1]) // 2), 5,(255,255,255), -1)
                else :
                        print("О Ш И Б К А\nВы выбрали две одинаковые клетки !!!")
        cv.imwrite('png\\data' + str(pathcount) +'.png', img)
        return 'png\\data' + str(pathcount) +'.png'
