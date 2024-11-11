import cv2
from tensorflow.keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import face_recognition
import os
import time

# Cargar el modelo de emociones y el clasificador de rostros
model = load_model('models/emotion_model.keras')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Etiquetas de emociones y colores
emotion_labels = ['Asco', 'Enojado', 'Feliz', 'Miedo', 'Neutral', 'Sorpresa', 'Triste']
color_map = {
    'Asco': (0, 255, 255),  # Amarillo
    'Enojado': (0, 0, 255),  # Rojo
    'Feliz': (0, 255, 0),    # Verde
    'Miedo': (255, 0, 0),    # Azul
    'Neutral': (255, 255, 255),  # Blanco
    'Sorpresa': (255, 0, 255),   # Morado
    'Triste': (128, 128, 128)    # Gris
}
emotion_counts = Counter()

# Cargar imágenes de referencia para el reconocimiento de personas
known_face_encodings = []
known_face_names = []
for filename in os.listdir("known_faces"):
    image_path = os.path.join("known_faces", filename)
    known_image = face_recognition.load_image_file(image_path)
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    known_face_encodings.append(known_face_encoding)
    known_face_names.append(os.path.splitext(filename)[0])

# Configuración de captura de video y tiempo de inicio
cap = cv2.VideoCapture(0)
frame_count = 0
frame_skip = 30  # Procesar solo cada 5 fotogramas
plot_update_interval = 30
session_start_time = time.time()  # Tiempo de inicio de la sesión

plt.ion()  # Modo interactivo de matplotlib

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    # Procesar solo cada 'frame_skip' fotogramas
    if frame_count % frame_skip == 0:
        # Redimensionar el frame para acelerar procesamiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detectar y reconocer rostros
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Comparar con caras conocidas usando distancias en lugar de comparaciones directas
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            name = "Desconocido"
            if distances[best_match_index] < 0.6:
                name = known_face_names[best_match_index]

            # Ajustar coordenadas de vuelta al tamaño original
            top, right, bottom, left = top * 2, right * 2, bottom * 2, left * 2
            roi_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[top:bottom, left:right]
            roi_gray = cv2.resize(roi_gray, (48, 48))
            roi = roi_gray.astype('float32') / 255.0
            roi = np.expand_dims(roi, axis=0)
            roi = np.expand_dims(roi, axis=-1)

            # Predecir emoción
            prediction = model.predict(roi)
            max_index = np.argmax(prediction)
            predicted_emotion = emotion_labels[max_index]
            emotion_counts[predicted_emotion] += 1

            # Mostrar cuadro y texto
            cv2.rectangle(frame, (left, top), (right, bottom), color_map.get(predicted_emotion, (255, 255, 255)), 2)
            cv2.putText(frame, f'{name} - {predicted_emotion}', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Mostrar el video en pantalla
    cv2.imshow('Emotion and Face Recognition', frame)

    # Solo actualizar el gráfico cada 'plot_update_interval' fotogramas
    if frame_count % plot_update_interval == 0:
        session_duration = time.time() - session_start_time
        session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

        plt.clf()
        plt.bar(emotion_counts.keys(), emotion_counts.values(), color='blue')
        plt.xlabel('Emociones')
        plt.ylabel('Frecuencia')
        plt.title(f"Duración de la sesión: {session_duration_formatted}")
        plt.draw()
        plt.pause(0.01)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Calcular la duración final de la sesión
session_duration = time.time() - session_start_time
session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

# Guardar el gráfico final en un archivo PNG
plt.clf()
plt.bar(emotion_counts.keys(), emotion_counts.values(), color='blue')
plt.xlabel('Emociones')
plt.ylabel('Frecuencia')
plt.title(f"Duración total de la sesión: {session_duration_formatted}")
plt.savefig("emotion_session_summary.png")

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()
