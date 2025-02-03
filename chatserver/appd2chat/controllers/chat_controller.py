from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from appd2chat.models.message import Message
from appd2chat.controllers.chat_client import ChatClient
from appd2chat.controllers.chat_client_facebook import FacebookClient # Import FacebookClient
import os
import re
import json
import mysql.connector
from datetime import datetime, timedelta  # Importar timedelta


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
    
@router.post("/eventos")
def get_eventos(mes: int = Query(..., ge=1, le=12)):
    try:
        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port=3306
        )
        cursor = mydb.cursor(dictionary=True)
        
        fecha_inicio = datetime.strptime(f"2025-{mes:02d}-01", '%Y-%m-%d')
        if mes == 12:
            fecha_fin = datetime.strptime("2026-01-01", '%Y-%m-%d')
        else:
            fecha_fin = datetime.strptime(f"2025-{mes + 1:02d}-01", '%Y-%m-%d')
        
        query = """
        SELECT * FROM eventos
        WHERE fecha >= %s AND fecha < %s
        """
        cursor.execute(query, (fecha_inicio, fecha_fin))
        results = cursor.fetchall()

        eventos_list = []
        for evento in results:
            eventos_list.append({
                'eventId': evento['id'],
                'eventDate': evento['fecha'].strftime('%Y-%m-%d'),
                'eventTitle': evento['evento'],
                'eventComittee': evento['comite'],              
                'eventType': evento['tipo_evento']
            })

        return JSONResponse(content=eventos_list)
    
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al conectar a la base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado: {e}")
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            cursor.close()
            mydb.close()
            
@router.post("/congregaciones")
def get_congregaciones():
    try:
        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port=3306
        )
        cursor = mydb.cursor(dictionary=True)

        query = "SELECT codigo, nombre FROM congregaciones" # Select only necessary columns
        cursor.execute(query)
        results = cursor.fetchall()

        congregaciones_list = [{'id': c['codigo'], 'nombre': c['nombre']} for c in results] # List comprehension for conciseness

        return JSONResponse(content=congregaciones_list)

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")
    finally:
        if mydb and mydb.is_connected():
            cursor.close()
            mydb.close()            


@router.post("/saverequest")
async def save_request(request: Request):
    try:
        data = json.loads(await request.body())
        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port=3306
        )
        cursor = mydb.cursor()

        query = "INSERT INTO portfolio_requests (services, congregations, startDate, endDate, budget, observations, userId, userChurch) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data.get('services'),
            data.get('congregations'),
            data.get('startDate'),
            data.get('endDate'),
            data.get('budget'),
            data.get('observations'),
            data.get('userId'),
            data.get('userChurch')
        )
        cursor.execute(query, values)
        mydb.commit()
        return JSONResponse(content={"message": "Request saved successfully"})
    except mysql.connector.Error as err:
        mydb.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON request body")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        mydb.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()

@router.post("/checkrequest")
async def check_request(request: Request):
    try:
        data = json.loads(await request.body())
        user_church = data.get('userChurch')
        service = data.get('service')
        current_date = data.get('currentDate')

        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port=3306
        )
        cursor = mydb.cursor()

        query = "SELECT COUNT(*) FROM portfolio_requests WHERE userChurch = %s AND services = %s AND endDate > %s"
        cursor.execute(query, (user_church, service, current_date))
        count = cursor.fetchone()[0]

        exists = count > 0
        return JSONResponse(content={"exists": exists})
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON request body")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()
            


@router.post("/getservicesrequest")
async def get_services_request(request: Request):
    try:
        body = await request.json()
        userId = body.get('userId')

        if userId is None:
            raise HTTPException(status_code=400, detail="Missing userId in request body")

        mydb = mysql.connector.connect(
            host="157.173.126.140",
            user="user_info_distrito_2",
            password="info*distrito2*db",
            database="informacion_distrito_2_db",
            port=3306
        )
        cursor = mydb.cursor(dictionary=True)

        query = """
        SELECT id, services, congregations, startDate, endDate, budget, observations, userId, userChurch, leadership_approval, pastor_approval
        FROM portfolio_requests
        WHERE userId = %s
        """
        cursor.execute(query, (userId,))
        results = cursor.fetchall()

        # Convertir los resultados a una lista de diccionarios
        services_request_list = []
        for r in results:
            # Convertir las fechas a cadenas
            r['startDate'] = r['startDate'].isoformat() if r['startDate'] else None
            r['endDate'] = r['endDate'].isoformat() if r['endDate'] else None
            
            # Convertir budget de Decimal a float
            r['budget'] = float(r['budget']) if r['budget'] is not None else None
            
            services_request_list.append(dict(r))

        return JSONResponse(content=services_request_list)

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")
    finally:
        if mydb and mydb.is_connected():
            cursor.close()
            mydb.close()
