import matplotlib.pyplot as plt
from collections import Counter
import time
import os
import csv  
from src.astra_connection import insert_emotion_data  
from src.api_connection import send_emotion_data  
import base64


emotion_counts = Counter()
session_start_time = time.time()

plt.ion()  # Modo interactivo de matplotlib

def update_plot():
    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    plt.clf()
    plt.bar(emotion_counts.keys(), emotion_counts.values(), color='blue')
    plt.xlabel('Emociones')
    plt.ylabel('Frecuencia')
    plt.title(f"Duración de la sesión: {session_duration_formatted}")
    plt.draw()
    plt.pause(0.01)

def save_final_plot(person_name="Desconocido"):
    # Crear la carpeta con el nombre de la persona si no existe
    directory = os.path.join("emotion_reports", person_name)
    os.makedirs(directory, exist_ok=True)

    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    plt.clf()
    plt.bar(emotion_counts.keys(), emotion_counts.values(), color='blue')
    plt.xlabel('Emociones')
    plt.ylabel('Frecuencia')
    plt.title(f"Duración total de la sesión: {session_duration_formatted}")

    # Guardar el gráfico en la carpeta correspondiente
    file_path = os.path.join(directory, "emotion_session_summary.png")
    plt.savefig(file_path)
    plt.ioff()
    plt.show()

    print(f"Gráfico guardado en: {file_path}")

def save_session_summary_to_csv(person_name):
    # Crear la carpeta con el nombre de la persona si no existe
    directory = os.path.join("emotion_reports", person_name)
    os.makedirs(directory, exist_ok=True)
    
    # Definir la ruta del archivo CSV
    csv_file_path = os.path.join(directory, "session_summary.csv")
    
    # Comprobar si el archivo CSV ya existe
    file_exists = os.path.isfile(csv_file_path)
    
    # Abrir el archivo CSV en modo de agregar y escribir el resumen de la sesión
    with open(csv_file_path, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        
        # Escribir el encabezado si el archivo es nuevo
        if not file_exists:
            writer.writerow(["timestamp", "session_duration"] + list(emotion_counts.keys()))
        
        # Escribir el resumen de la sesión
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        session_duration = time.time() - session_start_time
        session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))
        row = [timestamp, session_duration_formatted] + [emotion_counts[emotion] for emotion in emotion_counts.keys()]
        writer.writerow(row)

    print(f"Resumen de la sesión guardado en: {csv_file_path}")
    
def save_session_to_astra(person_name):
    # Preparar los datos para guardar en Astra
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    # Crear el documento con los datos de emociones
    document = {
        "name": person_name,
        "timestamp": timestamp,
        "session_duration": session_duration_formatted,
        "emotion_counts": dict(emotion_counts)  # Convertir Counter a diccionario
    }

    # Insertar el documento en la colección 'emotion_data' en Astra DB
    insert_emotion_data(document)
    # Preparar los datos para guardar en Astra
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    # Crear el documento con los datos de emociones
    document = {
        "name": person_name,
        "timestamp": timestamp,
        "session_duration": session_duration_formatted,
        "emotion_counts": dict(emotion_counts)  # Convertir Counter a diccionario
    }

    # Insertar el documento en la colección 'emotion_data' en Astra DB
    insert_emotion_data(document)
    


def save_session_to_api(person_name):
    # Preparar los datos para enviar a la API
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    session_duration = time.time() - session_start_time
    session_duration_formatted = time.strftime("%H:%M:%S", time.gmtime(session_duration))

    # Ruta del gráfico guardado
    file_path = f"emotion_reports/{person_name}/emotion_session_summary.png"
    # Codificar el gráfico en base64

    # Crear el payload con los datos de emociones y el gráfico en base64
    payload = {
        "name": person_name,
        "timestamp": timestamp,
        "session_duration": session_duration_formatted,
        "emotion_counts": dict(emotion_counts),  # Convertir Counter a diccionario
    }

    # Llamar a la función para enviar los datos a la API
    send_emotion_data(payload)