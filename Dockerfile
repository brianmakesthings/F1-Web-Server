FROM python:3.8
RUN mkdir /app 

RUN mkdir /f1_cache
RUN mkdir /app/bin
COPY . /
WORKDIR /
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
EXPOSE 80
CMD [ "python", "manage.py", "runserver", "0.0.0.0:80" ]


