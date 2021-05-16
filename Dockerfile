FROM python:3.8

VOLUME /API
EXPOSE 5000
COPY requeriments.txt /tmp
RUN pip install -r /tmp/requeriments.txt
WORKDIR /API
COPY . .
CMD [ "python", "app.py" ]