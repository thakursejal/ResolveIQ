FROM python:3.11-slim

RUN pip install --no-cache-dir hindsight

EXPOSE 8888

CMD ["hindsight", "serve", "--host", "0.0.0.0", "--port", "8888"]
