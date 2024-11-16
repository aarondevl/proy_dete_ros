import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import cv2
import numpy as np
import mss
from src.emotion_recognition import predict_emotion
from src.visualization import (
    record_emotion, 
    create_session_directory, 
    save_session_summary,
    save_session_to_astra
)
import time

# Configuración
sct = mss.mss()
monitor = sct.monitors[2]
frame_count = 0
frame_skip = 15
running = True

# Cargar el clasificador de cascada
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if face_cascade.empty():
    raise Exception("Error al cargar el clasificador de cascada")

print("=== Sistema de Detección de Emociones ===")
print("Iniciando captura de video...")
print("Presiona 'q' para finalizar la sesión")
print("=======================================")

# Crear directorio de sesión
session_dir, faces_dir, plots_dir = create_session_directory()
print(f"Sesión iniciada: {os.path.basename(session_dir)}")

try:
    while running:
        try:
            # Capturar pantalla y convertir correctamente
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            frame_count += 1
            if frame_count % frame_skip == 0:
                # Detectar rostros
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=4,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                # Procesar cada rostro
                for (x, y, w, h) in faces:
                    try:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        roi_gray = gray[y:y+h, x:x+w]
                        
                        if roi_gray.size > 0:
                            roi_gray = cv2.resize(roi_gray, (48, 48))
                            predicted_emotion = predict_emotion(roi_gray)
                            
                            # Registrar emoción
                            person_id = record_emotion(frame, x, y, w, h, predicted_emotion, faces_dir)
                            
                            if person_id:
                                # Mostrar información en pantalla
                                text = f"{person_id}: {predicted_emotion}"
                                cv2.putText(frame, text, 
                                          (x, y-10), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 
                                          0.9, (0, 255, 0), 2)
                                
                    except Exception as e:
                        print(f"Error al procesar un rostro: {e}")
                        continue

            # Mostrar frame
            cv2.imshow('Detección de Emociones', frame)

            # Verificar tecla de salida
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nFinalizando sesión...")
                running = False

        except Exception as e:
            print(f"Error en el bucle principal: {e}")
            time.sleep(1)  # Pausa para evitar bucle infinito de errores
            continue

except KeyboardInterrupt:
    print("\nDetección interrumpida por el usuario")
except Exception as e:
    print(f"\nError inesperado: {e}")
finally:
    print("\nGuardando datos de la sesión...")
    try:
        save_session_summary(session_dir, faces_dir, plots_dir)
        save_session_to_astra("Reunión")
        print(f"Datos guardados en: {session_dir}")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
    
    print("Cerrando ventanas...")
    cv2.destroyAllWindows()
    print("Sesión finalizada")