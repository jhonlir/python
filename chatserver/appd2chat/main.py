from fastapi import FastAPI
from appd2chat.controllers.chat_controller import router as chat_router

app = FastAPI()

app.include_router(chat_router)

