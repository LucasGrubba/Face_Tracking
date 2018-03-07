import cv2

# Determina o tamanho da janela de captura
cap = cv2.VideoCapture(0)
cap.set(3, 640) #largura
cap.set(4, 480) #altura

# Local do haarcascade para reconhecimento de rostos
face_cascade = cv2.CascadeClassifier('..\\opencv\\sources\\data\\haarcascades\\haarcascade_frontalface_default.xml')

while(True):
    # Captura a imagem frame por frame
    ret, frame = cap.read()

    # Detecta o rosto com base na classificação contida no haarcascade selecionado
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    print(len(faces))
    
    # Mostra o resultado da detecção
    for (x,y,w,h) in faces:
         cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
         roi_gray = gray[y:y+h, x:x+w]
         roi_color = frame[y:y+h, x:x+w]

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
