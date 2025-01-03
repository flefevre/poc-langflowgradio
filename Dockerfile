FROM python:3.11-slim
WORKDIR /app



EXPOSE 7870
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7870

# Installer curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install --upgrade pip

COPY ./requirements_gradio.txt/ .
RUN pip install --no-cache-dir -r requirements_gradio.txt
#RUN pip install -r requirements_gradio.txt

COPY . .

CMD ["python", "app.py"]