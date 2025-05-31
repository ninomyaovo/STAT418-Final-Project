FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the source code
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "api.py"]
