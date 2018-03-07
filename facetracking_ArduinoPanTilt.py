import cv2
import numpy as np
import serial
import struct
from time import sleep

# Define a janela de captura
cap = cv2.VideoCapture(0)
cap.set(3, 640) #largura
cap.set(4, 480) #altura

# Configura comunicação Serial
serialConnection = serial.Serial('COM4', 9600)

# Localiza haarcascade para detecccao de rosto e olho
face_cascade = cv2.CascadeClassifier('C:\\Users\\lucas\\AppData\\Local\\Programs\\Python\\Python36-32\\Lib\\site-packages\\opencv\\sources\\data\\haarcascades\\haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('C:\\Users\\lucas\\AppData\\Local\\Programs\\Python\\Python36-32\\Lib\\site-packages\\opencv\\sources\\data\\haarcascades\\haarcascade_eye.xml')

# Definiçoes iniciais
tilt_chan = 0   # Canal de comunicaçao do tilt com Arduino
pan_chan = 1    # Canal de comunicaçao do pan com Arduino
cur_pan = 90    # Origem do pan
cur_tilt = 70   # origem do tilt
center_tolerance = 20   # Fator de tolerância para localizaçao do centro da captura
camera_fov_x = 42   # Angulo de visao da camera na positicao x
camera_fov_y = 50   # Angulo de visao da camera na posicao y

# Definiçao dos limites do servo
def setServo(pan, tilt):
    if pan < 0: pan = 0
    if pan > 180: pan = 180
    if tilt < 0: tilt = 0
    if tilt > 180: tilt = 180

    serialConnection.write(struct.pack('>BBBB',pan_chan,pan,tilt_chan,tilt))

# Calcula a nova posiçao do servo e grava em setServo para move-lo
def moveServo(direction, degrees):
    print ("Direction: %s  Degrees: %d" % (direction, degrees))
    global cur_pan
    global cur_tilt
    if direction=="LEFT":
       cur_pan = cur_pan + degrees
    if direction=="RIGHT":
       cur_pan = cur_pan - degrees
    if direction=="UP":
       cur_tilt = cur_tilt - degrees
    if direction=="DOWN":
       cur_tilt = cur_tilt + degrees

    setServo(cur_pan,cur_tilt)

# Inicializa posiçao do servo para o centro
def exerciseServo():
    setServo(0,90)
    sleep(1)
    setServo(180,0)
    sleep(1)
    setServo(180,180)
    sleep(1)
    setServo(0,180)
    sleep(1)
    setServo(90,75)

# Define pontos médios da imagem mostrando no debug
if cap.isOpened():
    x_res = cap.get(3)
    y_res = cap.get(4)
    cam_midpoint_x = x_res/2
    cam_midpoint_y = y_res/2

    print ("Confg de captura")
    print ("-----------------------")
    print (" X-Resolution: %d" % (x_res,))
    print (" Y-Resolution: %d" % (y_res,))
    print (" Cam Midpoint X: %d Y: %d" % (cam_midpoint_x, cam_midpoint_y))

# Testa os servos colocando na posicao inicial
exerciseServo()


while(True):
    # Captura a imagem da camera
    ret, frame = cap.read()

    # Inverte a imagem, efeito espelho
    frame = cv2.flip(frame, 1)

    # Detecta o rosto da pessoa
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    # Mostra o rosto detectado
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Define o ponto médio do rosto detectado
        face_midpoint_x = x+(w/2)
        face_midpoint_y = y+(h/2)

        # Calcula para onde a camera deve apontar com base no ponto medio da camera
        # do rosto detectado, os angulos do servo e os limites definidos no inicio

        if face_midpoint_y < (cam_midpoint_y - center_tolerance):
            degrees_per_move = int((cam_midpoint_y - face_midpoint_y) / (camera_fov_y/2))
            moveServo("UP", degrees_per_move)
        elif face_midpoint_y > (cam_midpoint_y + center_tolerance):
            degrees_per_move = int((face_midpoint_y - cam_midpoint_y) / (camera_fov_y/2))
            moveServo("DOWN", degrees_per_move)
        if face_midpoint_x > (cam_midpoint_x + center_tolerance):
            degrees_per_move = int((face_midpoint_x - cam_midpoint_x) / (camera_fov_x/2))
            moveServo("RIGHT", degrees_per_move)
        elif face_midpoint_x <  (cam_midpoint_x - center_tolerance):
            degrees_per_move = int((cam_midpoint_x - face_midpoint_x) / (camera_fov_x/2))
            moveServo("LEFT", degrees_per_move)

    # Mostra o resultado da captura
    cv2.imshow('frame',frame)

    # Encerra caso aperte a letra q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Encerra tudo
cap.release()
cv2.destroyAllWindows()
serialConnection.close()
