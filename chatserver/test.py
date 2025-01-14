import json
import re  # Importar el módulo re para expresiones regulares

class ResponseParser:
    def __init__(self, json_data):
        self.code = json_data.get('code')
        self.message = json_data.get('message')
        self.conversation_id = json_data.get('conversation_id')

    def parse_message(self):
        try:
            # Limpiar la cadena JSON para eliminar caracteres de formato innecesarios
            cleaned_json_str = self.message.replace("```json", "").replace("```", "").replace("\\n", "").strip()
            
            # Reparar caracteres de escape en la cadena JSON
            cleaned_json_str = re.sub(r'\\{2,}(\\")', r'\1', cleaned_json_str)
            
            # Eliminar dobles comillas innecesarias que rodean la cadena JSON
            if cleaned_json_str.startswith('"') and cleaned_json_str.endswith('"'):
                cleaned_json_str = cleaned_json_str[1:-1]
            
            # Reemplazar comillas escapadas con comillas regulares
            cleaned_json_str = cleaned_json_str.replace('\\"', '"')
            
            # Reemplazar otros caracteres de escape
            cleaned_json_str = cleaned_json_str.replace("\\", "")
            
            # Convertir la cadena limpiada en un objeto JSON
            tmp_response = json.loads(cleaned_json_str)
            
            return tmp_response['rta_alterna']
        except json.JSONDecodeError as e:
            return f"Error: Invalid response format - {str(e)}"

# JSON proporcionado
json_str = '''{
    "code": 200,
    "message": "```json\\n{\\n  \\"opcion\\": \\"4\\",\\n  \\"sql\\": \\"no aplica\\",\\n  \\"rta_alterna\\": \\"La frase \\\\\\"como savemos que estamos con buena salut?\\\\\\" tiene errores. La forma correcta es: \\\\\\"¿Cómo sabemos que estamos con buena salud?\\\\\\"\\n```",
    "conversation_id": "2d614b34-018c-4221-8555-fb31686273bf"
}'''

# Convertir la cadena JSON a un diccionario
json_data = json.loads(json_str)

# Crear una instancia de ResponseParser
parser = ResponseParser(json_data)

# Intentar parsear el campo message
parsed_message = parser.parse_message()

# Imprimir el resultado
print(f"Parsed Message: {parsed_message}")
