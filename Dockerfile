FROM python:3.7-alpine

WORKDIR /app

RUN apk add libxml2-dev libxslt-dev build-base
RUN pip install pipenv
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

RUN pipenv install

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]