import cv2
import time
import numpy as np
import mss
from src.emotion_recognition import predict_emotion
from src.face_recognition_utils import load_known_faces, recognize_face
from src.visualization import update_plot, save_final_plot, save_session_summary_to_csv, save_session_to_astra, emotion_counts, save_session_to_api

# Configuración de captura de pantalla completa
sct = mss.mss()
monitor = sct.monitors[2]  # Monitor principal, cambiar a sct.monitors[2] si usas más monitores
frame_count = 0
frame_skip = 30  # Procesar solo cada 30 fotogramas
plot_update_interval = 30

# Cargar caras conocidas
load_known_faces()

person_name = "Desconocido"

while True:
    # Capturar toda la pantalla
    screenshot = sct.grab(monitor)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convertir de BGRA a BGR para usarlo con OpenCV

    frame_count += 1
    if frame_count % frame_skip == 0:
        # Reducir la resolución de la imagen para acelerar el procesamiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Reconocer rostros en la imagen capturada
        recognized_faces = recognize_face(rgb_frame)

        for (top, right, bottom, left, name) in recognized_faces:
            person_name = name  # Guardar el nombre de la persona reconocida
            # Ajustar las coordenadas al tamaño original
            top, right, bottom, left = top * 2, right * 2, bottom * 2, left * 2
            roi_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[top:bottom, left:right]
            roi_gray = cv2.resize(roi_gray, (48, 48))

            predicted_emotion = predict_emotion(roi_gray)
            emotion_counts[predicted_emotion] += 1

            # Dibujar el rectángulo y poner la etiqueta en la pantalla capturada
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), 2)
            cv2.putText(frame, f'{name} - {predicted_emotion}', (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Mostrar la pantalla con los rostros reconocidos
    cv2.imshow('Emotion and Face Recognition on Screen', frame)

    # Actualizar el gráfico cada cierto intervalo de fotogramas
    if frame_count % plot_update_interval == 0:
        update_plot()

    # Salir si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Guardar el gráfico, el resumen de la sesión en CSV, y enviar a Astra
save_final_plot(person_name)
save_session_summary_to_csv(person_name)
save_session_to_astra(person_name)
save_session_to_api(person_name)

cv2.destroyAllWindows()
