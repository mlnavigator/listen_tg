FROM python:3.12-slim

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["python", "-u", "/app/listen.py"]