FROM python:3.13-slim

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main_service.main:app", "--host", "0.0.0.0", "--port", "8001"]