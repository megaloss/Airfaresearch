FROM python:3.8-alpine

# install back-end
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY * /app/
#run the app on https
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000",  "--ssl-keyfile", "/cert/privkey.pem", "--ssl-certfile", "/cert/fullchain.pem"]

EXPOSE 8000
