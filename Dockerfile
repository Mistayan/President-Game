# Dockerfile
FROM python:3.11-alpine3.18
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip wheel setuptools
RUN python -m venv venv
RUN ./venv/bin/pip install -r requirements.txt
ENV FLASK_APP=GameServer
EXPOSE 5001
CMD ["./venv/bin/python", "run_server.py"]
