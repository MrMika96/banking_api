FROM python:3.11.6-slim-bullseye

COPY ["pyproject.toml", "poetry.lock", "./"]

RUN pip install --upgrade pip setuptools wheel poetry && \
    rm -rf /root/.cache/pip && \
    rm -rf /root/.cache/pypoetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

ENV DB_NAME="practiceDB"
ENV DB_USER="practiceUser"
ENV DB_PASSWORD="practicePw"
ENV DB_HOST="127.0.0.1"
ENV DB_PORT="5455"

CMD [ "python3 manage.py runserver"]