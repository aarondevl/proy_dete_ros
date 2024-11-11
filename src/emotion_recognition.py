import numpy as np
from tensorflow.keras.models import load_model

# Cargar el modelo de emociones
model = load_model('models/emotion_model.keras')
emotion_labels = ['Asco', 'Enojado', 'Feliz', 'Miedo', 'Neutral', 'Sorpresa', 'Triste']

def predict_emotion(roi):
    roi = roi.astype('float32') / 255.0
    roi = np.expand_dims(roi, axis=0)
    roi = np.expand_dims(roi, axis=-1)
    prediction = model.predict(roi)
    max_index = np.argmax(prediction)
    return emotion_labels[max_index]
