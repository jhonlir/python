from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from appd2chat.models.message import Message
from appd2chat.controllers.chat_client import ChatClient
from appd2chat.controllers.chat_client_facebook import FacebookClient # Import FacebookClient
import os
import re
import json
import mysql.connector


router = APIRouter()

@router.post("/chatserver")
async def chat(message: Message):
    # Leer el archivo instrucciones.txt
    instructions_file_path = '/app/instrucciones.txt'
    with open(instructions_file_path, 'r') as file:
        message_template = file.read()
    
    # Reemplazar '_m_e_n_s_a_j_e_' con el contenido de message.message
    completed_message = message_template.replace('_m_e_n_s_a_j_e_', message.message)

    

    client = ChatClient()
    
    # Establecer conversation_id si está presente en el mensaje
    if message.conversation_id:
        client.set_conversation_id(message.conversation_id)
    
    result = client.send_message(completed_message)
    msg = ' ';
    if result:
        message_content = result['important_response']   
        datos = extract_option_sql(message_content);
        
        if datos:
            option = datos['opcion']
            if option == '1':                
                msg = process_sql(datos['sql'])
                print(msg)
            elif option == '2':
                print("Dos")
            elif option == '3':
                print("Tres")
            elif option == '4':
                print("Cuatro")
            else:
                print(f"Opción no reconocida: {option}")
        else:
            print("No se pudo extraer la opción y la sentencia SQL.")
    
    
        response = {
            "code": 200,
            "message": msg,  # Usar tmp_response.rta_alterna como valor para la propiedad message
            "conversation_id": result['conversation_id']
        }
    else:
        response = {
            "code": 500,
            "message": "Error processing the request"
        }
    # Forzar la conversión a UTF-8 antes de devolver la respuesta 
    #return JSONResponse(content=json.dumps(response, ensure_ascii=False).encode('utf-8'), headers={"Content-Type": "application/json; charset=utf-8"})
    return JSONResponse(content=response, headers={"Content-Type": "application/json; charset=utf-8"})
    
    
@router.post("/facebook/video")
def get_facebook_video_embed(video_id: str, client: FacebookClient = Depends(FacebookClient)):
    try:
        embed_html = client.get_video_embed_html(video_id)
        return JSONResponse(content={'embedHtml': embed_html})
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions for proper FastAPI error handling
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
        
def extract_option_sql(input_string):
    match = re.match(r"\[opcion:(\d+)\]\[sql:(.*)\]", input_string)  # Expresión regular corregida
    if match:
        option = match.group(1)
        sql = match.group(2)
        return {"opcion": option, "sql": sql}
    else:
        return None        
        
        
import mysql.connector

def process_sql(sql_query):
    new_sql = sql_query.replace('*', "CONCAT_WS(', ', CONCAT(nombre,' ', apellidos), numero_celular) AS '-> '", 1)
    try:
        # Usando expresiones regulares para reemplazar los espacios múltiples dentro de los signos de porcentaje por %
        new_sql = re.sub(r'%(.*?)%', lambda match: '%' + re.sub(r'\s+', '%', match.group(1).strip()) + '%', new_sql)
        print(f"Uno: {new_sql}")
        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port= 3306
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(new_sql)
        results = cursor.fetchall()

        output_list = ['Ésta es la información que puedo proveerte: ']
        for row in results:
            row_string = ""
            for key, value in row.items():
                row_string += f"{key} {value}, "
            output_list.append(row_string.strip(", "))
        return output_list
    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            cursor.close()
            mydb.close()        