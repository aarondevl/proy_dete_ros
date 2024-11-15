import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import time
import os
import csv
import json
from datetime import datetime
import uuid
import cv2
import face_recognition
from src.astra_connection import insert_emotion_data

# Variables globales
emotion_history = defaultdict(list)
known_face_encodings = []
known_face_ids = []
face_images = {}
last_person_id = 0
session_start_time = time.time()

def create_session_directory():
    """Crea un directorio único para la sesión actual"""
    base_dir = "emotion_reports"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = str(uuid.uuid4())[:8]  # Usar los primeros 8 caracteres del UUID
    session_name = f"session_{timestamp}_{session_id}"
    
    # Crear estructura de directorios
    session_dir = os.path.join(base_dir, session_name)
    faces_dir = os.path.join(session_dir, "faces")
    plots_dir = os.path.join(session_dir, "plots")
    
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(faces_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    return session_dir, faces_dir, plots_dir

def get_person_id(frame, x, y, w, h, faces_dir):
    """
    Determina el ID de la persona y guarda su imagen
    """
    global last_person_id
    
    face_image = frame[y:y+h, x:x+w]
    face_encoding = face_recognition.face_encodings(face_image)
    
    if len(face_encoding) == 0:
        return None
        
    face_encoding = face_encoding[0]
    
    if known_face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        
        if True in matches:
            first_match_index = matches.index(True)
            return known_face_ids[first_match_index]
    
    # Si es una cara nueva
    new_person_id = f"person_{last_person_id}"
    last_person_id += 1
    
    # Guardar encoding e ID
    known_face_encodings.append(face_encoding)
    known_face_ids.append(new_person_id)
    
    # Guardar imagen de la cara
    if not os.path.exists(os.path.join(faces_dir, f"{new_person_id}")):
        os.makedirs(os.path.join(faces_dir, f"{new_person_id}"))
    
    # Guardar la primera imagen y algunas actualizaciones
    timestamp = datetime.now().strftime("%H%M%S")
    image_path = os.path.join(faces_dir, f"{new_person_id}", f"{timestamp}.jpg")
    cv2.imwrite(image_path, face_image)
    
    # Guardar también una imagen de referencia
    ref_image_path = os.path.join(faces_dir, f"{new_person_id}", "reference.jpg")
    if not os.path.exists(ref_image_path):
        cv2.imwrite(ref_image_path, face_image)
    
    return new_person_id

def record_emotion(frame, x, y, w, h, emotion, faces_dir):
    """Registra una emoción en el historial de la persona"""
    person_id = get_person_id(frame, x, y, w, h, faces_dir)
    
    if person_id is not None:
        emotion_history[person_id].append({
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion,
            'session_time': time.time() - session_start_time
        })
    
    return person_id

def generate_emotion_plots(directory):
    """Genera gráficos de emociones para cada persona al final de la sesión"""
    # Configuración del estilo básico
    plt.style.use('default')
    
    # Gráfico individual para cada persona
    for person_id, emotions in emotion_history.items():
        if len(emotions) > 0:
            plt.figure(figsize=(12, 6))
            timestamps = [entry['session_time'] for entry in emotions]
            emotion_values = [entry['emotion'] for entry in emotions]
            
            plt.plot(timestamps, emotion_values, 'o-', linewidth=2, markersize=8)
            plt.title(f'Emociones detectadas - {person_id}')
            plt.xlabel('Tiempo de sesión (segundos)')
            plt.ylabel('Emoción')
            plt.grid(True, alpha=0.3)
            
            # Ajustar los márgenes
            plt.tight_layout()
            
            # Guardar el gráfico
            plt.savefig(os.path.join(directory, f"{person_id}_emotions.png"), 
                       bbox_inches='tight', 
                       dpi=300)
            plt.close()
    
    # Gráfico combinado de todas las personas
    plt.figure(figsize=(15, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, len(emotion_history)))
    
    for (person_id, emotions), color in zip(emotion_history.items(), colors):
        if len(emotions) > 0:
            timestamps = [entry['session_time'] for entry in emotions]
            emotion_values = [entry['emotion'] for entry in emotions]
            plt.plot(timestamps, emotion_values, 'o-', 
                    label=person_id, 
                    color=color, 
                    alpha=0.7,
                    linewidth=2,
                    markersize=6)
    
    plt.title('Historial de Emociones - Todas las Personas')
    plt.xlabel('Tiempo de sesión (segundos)')
    plt.ylabel('Emoción')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Guardar el gráfico combinado
    plt.savefig(os.path.join(directory, "all_emotions.png"), 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def save_session_summary(session_dir, faces_dir, plots_dir):
    """Guarda el resumen de la sesión completa"""
    # Generar gráficos
    generate_emotion_plots(plots_dir)
    
    # Guardar CSV con el historial
    csv_path = os.path.join(session_dir, "emotion_history.csv")
    with open(csv_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "person_id", "emotion", "session_time_seconds"])
        
        for person_id, emotions in emotion_history.items():
            for entry in emotions:
                writer.writerow([
                    entry['timestamp'],
                    person_id,
                    entry['emotion'],
                    f"{entry['session_time']:.2f}"
                ])
    
    # Guardar JSON con datos completos
    session_data = {
        "session_id": os.path.basename(session_dir),
        "timestamp": datetime.now().isoformat(),
        "session_duration": time.strftime("%H:%M:%S", time.gmtime(time.time() - session_start_time)),
        "participants": []
    }
    
    for person_id, emotions in emotion_history.items():
        if len(emotions) > 0:
            emotion_freq = defaultdict(int)
            for entry in emotions:
                emotion_freq[entry['emotion']] += 1
                
            participant_data = {
                "person_id": person_id,
                "emotion_history": emotions,
                "emotion_frequencies": dict(emotion_freq),
                "total_detections": len(emotions),
                "first_detection": emotions[0]['timestamp'],
                "last_detection": emotions[-1]['timestamp'],
                "detection_duration_seconds": emotions[-1]['session_time'] - emotions[0]['session_time']
            }
            session_data["participants"].append(participant_data)
    
    json_path = os.path.join(session_dir, "session_data.json")
    with open(json_path, "w") as f:
        json.dump(session_data, f, indent=4)

def save_session_to_astra(session_name):
    """
    Guarda los datos de la sesión en Astra DB, incluyendo información detallada
    de cada participante y sus emociones
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    # Preparar datos de participantes
    participants_data = []
    for person_id, emotions in emotion_history.items():
        if len(emotions) > 0:
            # Calcular frecuencia de emociones para esta persona
            emotion_freq = defaultdict(int)
            for entry in emotions:
                emotion_freq[entry['emotion']] += 1

            # Datos del participante
            participant = {
                "person_id": person_id,
                "emotion_frequencies": dict(emotion_freq),
                "total_detections": len(emotions),
                "first_detection": emotions[0]['timestamp'],
                "last_detection": emotions[-1]['timestamp'],
                "detection_duration_seconds": emotions[-1]['session_time'] - emotions[0]['session_time'],
                "emotion_timeline": [
                    {
                        "emotion": entry['emotion'],
                        "timestamp": entry['timestamp'],
                        "session_time": entry['session_time']
                    }
                    for entry in emotions
                ]
            }
            participants_data.append(participant)

    # Crear el documento principal
    document = {
        "session_name": session_name,
        "timestamp": timestamp,
        "session_duration": session_duration_formatted,
        "total_participants": len(participants_data),
        "session_id": str(uuid.uuid4()),  # Identificador único para la sesión
        "participants": participants_data,
        "metadata": {
            "total_detections": sum(len(emotions) for emotions in emotion_history.values()),
            "average_detections_per_person": sum(len(emotions) for emotions in emotion_history.values()) / len(emotion_history) if emotion_history else 0,
            "creation_date": datetime.now().isoformat(),
            "version": "2.0"
        }
    }

    try:
        # Insertar en Astra DB
        insert_emotion_data(document)
        print(f"Datos guardados exitosamente en Astra DB para la sesión: {session_name}")
        
        # Guardar copia de respaldo en JSON
        backup_path = os.path.join("emotion_reports", session_name, "astra_backup.json")
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with open(backup_path, "w") as f:
            json.dump(document, f, indent=4)
        print(f"Copia de respaldo guardada en: {backup_path}")
        
    except Exception as e:
        print(f"Error al guardar en Astra DB: {e}")
        print("Guardando solo copia de respaldo...")
        backup_path = os.path.join("emotion_reports", session_name, "astra_backup.json")
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with open(backup_path, "w") as f:
            json.dump(document, f, indent=4)
        print(f"Copia de respaldo guardada en: {backup_path}")
