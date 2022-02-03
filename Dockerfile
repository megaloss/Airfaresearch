FROM python:3.8-alpine

# install back-end
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
COPY *.py /app/
COPY airports.p /app/
RUN pip3 install -r requirements.txt



CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

#start back
#CMD ["gunicorn", "-w 4", "main:app", "-b", "0.0.0.0:8000"]
# CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:8000", "main:app"]

#open ports
# EXPOSE 80
# EXPOSE 8000