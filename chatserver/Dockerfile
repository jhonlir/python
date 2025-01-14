FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

COPY ./appd2chat /app/appd2chat
COPY ./requirements.txt /app/requirements.txt
COPY ./gunicorn_config.py /app/gunicorn_config.py
COPY ./instrucciones.txt /app/instrucciones.txt

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

CMD ["gunicorn", "-c", "/app/gunicorn_config.py", "appd2chat.main:app"]
