import cv2
import os
# Obtener la ruta absoluta del archivo XML
xml_path = os.path.abspath('./src/xml/haarcascade_frontalface_default.xml')

# Cargar el clasificador de Haar usando la ruta absoluta
face_cascade = cv2.CascadeClassifier(xml_path)

def detect_faces(frame):
    # Convertir la imagen a escala de grises para la detección
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros en la imagen
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.03,  # Reduce a 1.05 o incluso 1.03 para mayor sensibilidad
        minNeighbors=3,    # Baja a 3 para incrementar la detección
        minSize=(30, 30)   # Tamaño mínimo del rostro a detectar
    )
    
    # Devolver la lista de coordenadas de los rostros detectados
    return faces
