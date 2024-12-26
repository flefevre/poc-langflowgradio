FROM python:3.10-slim

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir gradio requests
EXPOSE 7870
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7870

CMD ["python", "app.py"]