FROM python:3.7-alpine
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install pipenv

RUN pipenv install

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]