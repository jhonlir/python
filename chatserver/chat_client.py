import requests
import json

class ChatClient:
    def __init__(self):
        self.session_urlx = 'http://appd2.online:81/api/chat/sessions'
        self.chat_urlx = 'http://appd2.online:81/api/chat?client=web'
        
        self.session_url = 'https://app.khoj.dev/api/chat/sessions'
        self.chat_url = 'https://app.khoj.dev/api/chat?client=web'
        self.token = 'kk-tmdyi-ngeX2BSpQ4hYG7witjWIPYfh5BPzfK7nJS6eM';
        
        
        
    def send_message(self, mensaje):
        
        headers = { "Authorization": f"Bearer {self.token}", "Content-Type": "application/json" }
        datax = { }
        
        # Realizar la primera petición para obtener el conversation_id
        
        response = requests.post(self.session_url, headers=headers, json=datax)
        print(f"Respuesta cruda de la primera petición: {response.text}")
        
        try:
            response_data = response.json()
            conversation_id = response_data.get('conversation_id')

            if not conversation_id:
                raise ValueError('No se pudo obtener el conversation_id')

            # Configurar los datos y las cabeceras para la segunda petición
            headers = {
                'Authorization': f'Bearer {conversation_id}',
                'Accept-Language': 'application/json'
            }
            data = {
                'city': 'Bogota',
                'conversation_id': conversation_id,
                'country': 'CO',
                'q': mensaje,
                'region': 'Bogota D.C.',
                'stream': True,
                'timezone': 'America/Bogota'
            }

            # Realizar la segunda petición utilizando el conversation_id
            response = requests.post(self.chat_url, json=data, headers=headers)
            print(f"Respuesta cruda de la segunda petición: {response.text}")

            # Reemplazar caracteres especiales y dividir la respuesta en fragmentos
            response_text_clean = response.text.replace('␃🔚␗', '')
            fragments = response_text_clean.split('}')
            
            # Variables para almacenar la respuesta importante y otros objetos JSON
            important_response = ""
            more_objects = []
            capturing = False

            for fragment in fragments:
                fragment = fragment.strip()
                if fragment:
                    try:
                        json_fragment = json.loads(fragment + '}')
                        more_objects.append(json_fragment)
                        if json_fragment.get('type') == 'start_llm_response':
                            capturing = True
                        elif json_fragment.get('type') == 'end_llm_response':
                            capturing = False
                        else:
                            if capturing:
                                # Extraer y limpiar la respuesta importante
                                important_response += fragment.strip() + " "
                    except json.JSONDecodeError:
                        if capturing:
                            important_response += fragment.strip() + " "

            # Cortar el string hasta donde inicia {"type": "end_llm_response",
            end_response_index = important_response.find('{"type": "end_llm_response",')
            if end_response_index != -1:
                important_response = important_response[:end_response_index].strip()

            result = {
                "important_response": important_response,
                "more_objects": more_objects
            }
            print(f"Respuesta importante: {important_response}")
            print(f"Más objetos: {json.dumps(more_objects, indent=2)}")
            return result
        except ValueError as e:
            print(f"Error en la decodificación de JSON: {e}")
            return None
        except Exception as e:
            print(f"Error en la petición: {e}")
            return None

# Ejemplo de uso desde la línea de comando
if __name__ == "__main__":
    client = ChatClient()
    mensaje = "bien gracias, quiero saber si la siguiente frase está bien escrita: como savemos que estamos con buena salut?"
    respuesta = client.send_message(mensaje)
    # Imprimir los valores de los atributos por separado
    if respuesta:
        print("------------")
        print(f"Important Response: {respuesta['important_response']}")
        print("------------")
      #   print(f"More Objects: {json.dumps(respuesta['more_objects'], indent=2)}")
