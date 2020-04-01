import numpy
import cv2
import copy
import time
import os
import os.path


#print(path)
if os.path.exists('coordinates.txt'):
    user = input('Выберите режим работы: 1 - с текущими координатами; 2 - с заданными координатами ')
else:
     user = input('2 - с заданными координатами ')
    
ix = []
iy = []

call_counter=0
#Кликаем левой кнопкой и получаем кооординаты
def getCurrPoint(event,x,y,flags,param):
    global ix,iy
    global call_counter
    if event == cv2.EVENT_LBUTTONDBLCLK:
        call_counter += 1
        ix.append(x)
        iy.append(y)



cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
try:
    os.mkdir("images")
except FileExistsError:
    pass
ret, frame = cap.read()
frame_prev = copy.copy(frame)
h=480
w=640

cv2.namedWindow('frame')
if user == '2':
    time.sleep(2.5)  
    ret, frame = cap.read()
    time.sleep(2.5)
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    k = cv2.waitKey(500)
    cv2.setMouseCallback('frame',getCurrPoint)
    while call_counter != 6:

        cv2.imshow('frame', frame)
        k = cv2.waitKey(500)
    #Записываем координаты
    print('111',iy[1],iy[0],  ix[0],ix[1],  iy[3],iy[2],ix[2],ix[3])
    coord = open('coordinates.txt', 'w')
    if iy[1] > iy[0]:
        iy[1], iy[0] = iy[0], iy[1]
    if ix[0] > ix[1]:
        ix[0], ix[1] = ix[1], ix[0]
    if  iy[3] > iy[2]:
        iy[3], iy[2] = iy[2], iy[3]
    if ix[2] > ix[3]:
        ix[2], ix[3] = ix[3], ix[2]
    if iy[5] > iy[4]:
        iy[5], iy[4] = iy[4], iy[5]
    if ix[4] > ix[5]:
        ix[4], ix[5] = ix[5], ix[4]
        
  
    coord.write(str(ix[0])+ ' ' + str(iy[0]) + '\n')
    coord.write(str(ix[1])+ ' ' + str(iy[1]) + '\n')
    coord.write(str(ix[2]) + ' ' + str(iy[2]) + '\n')
    coord.write(str(ix[3]) + ' ' + str(iy[3]) + '\n')
    coord.write(str(ix[4]) + ' ' + str(iy[4]) + '\n')
    coord.write(str(ix[5]) + ' ' + str(iy[5]) + '\n')
    coord.close()
else:
    #Зачитываем координаты из файла
    file = open('coordinates.txt', 'r')
    for j in range(0, 6):
        text = file.readline()
        p1 = text.split()
        ix.append(int(p1[0]))
        iy.append(int(p1[1]))
    file.close()

listCar1=[]
listCar2=[]
listRail1=[]
listRail2=[]
state = 0

maxlistCar2 = 0 
minlistCar2 = 0
maxlistRail2 = 0
minlistRail2 = 0

while True:
#Размываем и получаем разность между кадрами
    
    ret, frame = cap.read() 
    frame = cv2.GaussianBlur(frame,(9,9),0)   
    frame2 = cv2.absdiff(frame, frame_prev)      
    frame_prev = copy.copy(frame)
    
   
    s1 = numpy.sum(frame2[iy[1]:iy[0], ix[0]:ix[1], 0:2])
    s2 = numpy.sum(frame2[iy[3]:iy[2], ix[2]:ix[3], 0:2])
    s3 = numpy.sum(frame2[iy[5]:iy[4], ix[4]:ix[5], 0:2])
    print(iy[1],iy[0],  ix[0],ix[1], s1, iy[3],iy[2],ix[2],ix[3], s2)
    #Находим среднее значение за секунду

    a = minlistCar2 + (0.2 * (maxlistCar2-minlistCar2))
    b = maxlistRail2 - 1
    range = (minlistRail2/10) + 1
    if len(listCar1)==80:
        listCar1.pop(0)
        
    listCar1.append((s1+s2)//1000)
    avgCar = (sum(listCar1) - max(listCar1) - min(listCar1))//78
        
    if len(listRail)==80:
        listRail1.pop(0)
    listRail1.append(s3//1000)
    avgRail = (sum(listRail1) - max(listRail1) - min(listRail1))//78
    


    #Находим мах и мин за час (7200)
    if len(listCar2)== 5000:#7200
        listCar2.pop(0)
    listCar2.append(avgCar)
    if len(listRail2)== 80:
        listRail2.pop(0)
    listRail2.append(avgRail)
    maxlistCar2 = max(listCar2)
    minlistCar2 = min(listCar2)
    maxlistRail2 = max(listRail2)
    minlistRail2 = min(listRail2)
    
        
    if len(listCar1)==80:
        if state == 0:
            if maxlistCar2 >= avgCar >= a:
                state = 0    
            else: 
                state = 1
        elif state == 1:
            if maxlistCar2 >= avgCar >= a:
                state = 0
            elif avgRail > b and (maxlistRail2 - minlistRail2) > range:
                state = 2
        elif state == 2:
            if maxlistCar2 >= avgCar >= a:
                state = 0
        
    #Соединяем точки и выводим области на кадр
    cv2.rectangle(frame, (ix[0],iy[0]), (ix[1], iy[1]),(0, 255, 0), 1)
    cv2.rectangle(frame2,(ix[0],iy[0]), (ix[1], iy[1]),(0, 255, 0), 1)
    cv2.rectangle(frame, (ix[2],iy[2]), (ix[3], iy[3]),(0, 255, 0), 1)
    cv2.rectangle(frame2,(ix[2],iy[2]), (ix[3], iy[3]),(0, 255, 0), 1)
    cv2.rectangle(frame, (ix[4],iy[4]), (ix[5], iy[5]),(0, 255, 0), 1)
    cv2.rectangle(frame2,(ix[4],iy[4]), (ix[5], iy[5]),(0, 255, 0), 1)
    # Вид шрифта:
    font = cv2.FONT_HERSHEY_COMPLEX

    photo = str(time.strftime('%d.%m.%y %H:%M:%S'))
    cv2.putText(frame, f'{photo} average = {avgCar},{avgRail}', (30,30), font, 1, color=(0, 0, 255), thickness=2)
    cv2.putText(frame, f'max = {maxlistCar2}, min = {minlistCar2}, len = {len(listCar2)}', (30,60), font, 1, color=(0, 0, 255), thickness=2)
    cv2.putText(frame, f'max = {maxlistRail2}, min = {minlistRail2}, len = {len(listRail2)}', (30,90), font, 1, color=(0, 0, 255), thickness=2)
    cv2.putText(frame, f'state = {state}', (30,120), font, 1, color=(0, 0, 255), thickness=2)

    
    time1 = str(time.strftime('%H%M%S'))
    cv2.imwrite(f'images/frame{time1}.jpg', frame)
    
    # Показать кадр
    cv2.imshow('frame', frame)
    cv2.imshow('frame2', frame2)
    k = cv2.waitKey(500)
    
    if k == ord('q'):
        break

cv2.waitKey()
cap.release()
cv2.destroyAllWindows()
