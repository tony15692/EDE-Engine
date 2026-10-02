FROM python:3.12-slim
WORKDIR /app
COPY . /app
EXPOSE 8899
CMD ["python","run.py","--host","0.0.0.0","--port","8899","--no-browser"]
