FROM nikolaik/python-nodejs:python3.7-nodejs10

RUN apt update
RUN apt install -y python3-dev gcc


WORKDIR /usr/src/app
COPY package*.json ./

RUN npm install
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python server.py serve
RUN npm start

EXPOSE 3000

CMD ["python", "server.py", "serve"]
