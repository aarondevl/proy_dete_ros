import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def load_data(data_dir, img_size=(48, 48), batch_size=32):
    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

    train_generator = datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        color_mode='grayscale',
        subset='training',
        shuffle=True)

    validation_generator = datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),  # Asume que la validación también está en train con un split
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        color_mode='grayscale',
        subset='validation',
        shuffle=False)

    return train_generator, validation_generator

def build_model():
    model = Sequential([
        Input(shape=(48, 48, 1)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(7, activation='softmax')  # Suponiendo 7 emociones posibles
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(data_dir):
    train_data, validation_data = load_data(data_dir)
    model = build_model()
    history = model.fit(train_data, epochs=50, validation_data=validation_data)
    model.save('/home/walocj/Proy_dete_ros/models/emotion_model.keras')  # Cambio aquí para guardar en formato .keras

if __name__ == '__main__':
    data_dir = '/home/walocj/Proy_dete_ros/data/KerasEmotion'  # Asegúrate de que el directorio es correcto
    train_model(data_dir)

