FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY simulador.py .

EXPOSE 8000 8001

CMD ["python", "-u", "simulador.py"]
