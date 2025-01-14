from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from appd2chat.models.message import Message
from appd2chat.controllers.chat_client import ChatClient
from appd2chat.controllers.chat_client_facebook import FacebookClient # Import FacebookClient
import os
import json

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

    if result:
        message_content = result['important_response']   
        response = {
            "code": 200,
            "message": message_content,  # Usar tmp_response.rta_alterna como valor para la propiedad message
            "conversation_id": result['conversation_id']
        }
    else:
        response = {
            "code": 500,
            "message": "Error processing the request"
        }

    return JSONResponse(content=response)
    
    
@router.post("/facebook/video")
def get_facebook_video_embed(video_id: str, client: FacebookClient = Depends(FacebookClient)):
    try:
        embed_html = client.get_video_embed_html(video_id)
        return JSONResponse(content={'embedHtml': embed_html})
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions for proper FastAPI error handling
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")