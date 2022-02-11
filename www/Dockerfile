FROM nginx:alpine
COPY . /usr/share/nginx/html/
COPY keys/* /etc/letsencrypt/
COPY runme.sh .
RUN chmod +x runme.sh
RUN sh ./runme.sh
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
EXPOSE 443
