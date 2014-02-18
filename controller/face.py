import time
import numpy as np
import cv2

face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')


def detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.circle(img, (x+w/2, y+h/2), w/2, (0,255,255), -1 )
        cv2.circle(img, (x+w/3, y+h/5), w/10, (0,0,0), -1 )
        cv2.circle(img, (x+2*w/3, y+h/5), w/10, (0,0,0), -1 )
        cv2.circle(img, (x+w/2, y+3*h/4), w/7, (0,0,0), -1 )
        cv2.circle(img, (x+w/2, y+h/2), w/2, (0,0,0), 3 )
    return img

cap = cv2.VideoCapture('rtsp://192.168.1.221:8554/')

skip = 1

while(cap.isOpened()):
    ret, frame = cap.read()
    skip += 1	
    if skip%3 == 0:
      #frame = detect(frame.copy())
      continue
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    	
cap.release()
cv2.destroyAllWindows()


#raspivid -hf -vf -t 999999 -h 768 -w1024 -fps 30 -o - | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264


