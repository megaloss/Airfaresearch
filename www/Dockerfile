FROM nginx:alpine
COPY * /usr/share/nginx/html/
COPY runme.sh .
RUN chmod +x runme.sh
RUN sh ./runme.sh