FROM python:3.11-slim

WORKDIR /app

# Copiar requirements.txt (desde el contexto ./flask_api/)
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . /app

CMD ["python", "app.py"]

EXPOSE 5000




