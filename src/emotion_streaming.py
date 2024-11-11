from flask import Flask, Response
import cv2
from tensorflow.keras.models import load_model
import numpy as np

app = Flask(__name__)
model = load_model('/home/walocj/Proy_dete_ros/models/emotion_model.keras')  # Asegúrate de que la ruta al modelo es correcta
emotion_labels = ['Asco', 'Enojado', 'Feliz', 'Miedo', 'Neutral', 'Sorpresa', 'Triste']

def gen_frames():  
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Procesamiento de detección de emociones
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48))
                roi = roi_gray.astype('float32')/255.0
                roi = np.expand_dims(roi, axis=0)
                roi = np.expand_dims(roi, axis=-1)
                prediction = model.predict(roi)
                max_index = np.argmax(prediction)
                predicted_emotion = emotion_labels[max_index]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, predicted_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Codificar el frame para streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.250.155', port=5000, debug=True)
