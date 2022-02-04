FROM python:3.8-alpine

# install back-end
RUN mkdir /app
WORKDIR /app
#COPY requirements.txt /app/
COPY * /app/
#COPY airports.p /app/
RUN pip3 install -r requirements.txt



CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000