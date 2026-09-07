FROM python:3.12-slim

WORKDIR /app

COPY requisitos.txt .
RUN pip install --no-cache-dir -r requisitos.txt

COPY aplicacion ./aplicacion

EXPOSE 8000

CMD ["uvicorn", "aplicacion.principal:app", "--host", "0.0.0.0", "--port", "8000"]
