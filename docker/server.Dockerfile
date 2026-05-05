FROM python:3.11-slim

WORKDIR /app

# зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# копируем проект
COPY . .

# создаём папки
RUN mkdir -p logs generated_qr

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
