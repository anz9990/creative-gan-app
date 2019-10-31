FROM python:3.6
FROM node:10

RUN apt update
RUN apt install -y python3-dev gcc


WORKDIR /usr/src/app
COPY package*.json ./

RUN npm install
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python app/server.py serve
RUN npm start

EXPOSE 3000

CMD ["python", "server.py", "serve"]
