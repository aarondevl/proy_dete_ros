import face_recognition
import os
import cv2
import numpy as np

# Cargar imágenes de referencia para el reconocimiento de personas
known_face_encodings = []
known_face_names = []

def load_known_faces(directory="known_faces"):
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)
        known_image = face_recognition.load_image_file(image_path)
        known_face_encoding = face_recognition.face_encodings(known_image)[0]
        known_face_encodings.append(known_face_encoding)
        known_face_names.append(os.path.splitext(filename)[0])

def recognize_face(rgb_frame):
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    recognized_faces = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(distances)
        name = "Desconocido"
        if distances[best_match_index] < 0.6:
            name = known_face_names[best_match_index]
        recognized_faces.append((top, right, bottom, left, name))
    
    return recognized_faces
