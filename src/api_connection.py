import requests


def send_emotion_data(payload):
    """
    Envía los datos de emociones a la API especificada.
    """
    url = 'https://magicloops.dev/api/loop/run/9824e3c7-4ced-4438-baff-97cf7ac882f1'
    
    try:
        response = requests.post(url, json=payload)
        
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            response_json = response.json()
            print(f"STATUS: {response_json['status']}")
            print(f"OUTPUT: {response_json['loopOutput']}")
        else:
            print(f"Error al enviar los datos. Código de estado: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error al conectar con la API: {e}")