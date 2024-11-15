import cv2
import os

# Obtener la ruta absoluta del archivo XML
xml_path = os.path.abspath('./src/xml/haarcascade_frontalface_default.xml')
print(f"Ruta del archivo XML: {xml_path}")  # Esto te permitirá ver la ruta que está siendo utilizada

# Cargar el clasificador de Haar usando la ruta absoluta
face_cascade = cv2.CascadeClassifier(xml_path)
