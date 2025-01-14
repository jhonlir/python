import requests
import json

class ChatClient:
    def __init__(self):
        
        self.session_urlx = 'http://appd2.online:81/api/chat/sessions'
        self.chat_urlx = 'http://appd2.online:81/api/chat?client=web'
        
        self.session_url = 'https://app.khoj.dev/api/chat/sessions'
        self.chat_url = 'https://app.khoj.dev/api/chat?client=web'
        self.token = 'kk-tmdyi-ngeX2BSpQ4hYG7witjWIPYfh5BPzfK7nJS6eM';          
        
        
        self.conversation_id = None  # Agregar atributo conversation_id

    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id

    def send_message(self, mensaje):
        headers = { "Authorization": f"Bearer {self.token}", "Content-Type": "application/json" }
        datax = { }        
        if not self.conversation_id:
           # Realizar la primera petición para obtener el conversation_id        
           response = requests.post(self.session_url, headers=headers, json=datax)            
           print(f"Respuesta cruda de la primera petición: {response.text}")
           try:
                response_data = response.json()
                self.conversation_id = response_data.get('conversation_id')
                if not self.conversation_id:
                    raise ValueError('No se pudo obtener el conversation_id')
           except ValueError as e:
                print(f"Error en la decodificación de JSON: {e}")
                return None
           except Exception as e:
                print(f"Error en la petición: {e}")
                return None

        headersx = {
            'Authorization': f'Bearer {self.conversation_id}',
            'Accept-Language': 'application/json'
        }
        data = {
            'city': 'Bogota',
            'conversation_id': self.conversation_id,
            'country': 'CO',
            'q': mensaje,
            'region': 'Bogota D.C.',
            'stream': True,
            'timezone': 'America/Bogota'
        }

        response = requests.post(self.chat_url, json=data, headers=headers)
        print(f"Respuesta cruda de la segunda petición: {response.text}")

        try:
            response_text_clean = response.text.replace('␃🔚␗', '')
            fragments = response_text_clean.split('}')

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
                                important_response += fragment.strip() + " "
                    except json.JSONDecodeError:
                        if capturing:
                            important_response += fragment.strip() + " "

            end_response_index = important_response.find('{"type": "end_llm_response",')
            if end_response_index != -1:
                important_response = important_response[:end_response_index].strip()

            result = {
                "important_response": important_response,
                "conversation_id": self.conversation_id
            }
            print(f"Respuesta importante: {important_response}")
            print(f"Más objetos: {json.dumps(self.conversation_id, indent=2)}")
            return result
        except Exception as e:
            print(f"Error en la petición: {e}")
            return None
