FROM python:3.8-alpine

# install back-end
RUN mkdir /app
WORKDIR /app
#COPY requirements.txt /app/
COPY * /app/
#COPY airports.p /app/
RUN pip3 install -r requirements.txt
RUN export TRANSAVIA_KEY=`aws ssm get-parameter --region eu-central-1 --name TRANS_API_KEY --output text --query Parameter.Value`


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000