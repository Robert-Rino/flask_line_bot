FROM python:3.7-alpine3.9
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000/tcp
CMD python -m flask run -h 0.0.0.0 -p 8000 --debugger