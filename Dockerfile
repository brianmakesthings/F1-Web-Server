FROM python:3.8

RUN apt-get update || : && apt-get install nodejs -y 
RUN apt-get install npm -y 

RUN mkdir /app 

RUN mkdir /f1_cache
RUN mkdir /app/bin
COPY . /
WORKDIR /
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
WORKDIR /jstoolchain
RUN npm install
RUN npm run tailwind-build
WORKDIR /
EXPOSE 80
CMD [ "python", "manage.py", "runserver", "0.0.0.0:80" ]


