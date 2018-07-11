FROM python:3.4
RUN mkdir /config
RUN mkdir /src
COPY requirements.txt /config
RUN pip install -r /config/requirements.txt
COPY src/ /src
ENV MODE='dev'
COPY src/utils/data_dump.json /src/utils

RUN chmod +x /src/utils/start.sh
RUN chmod +x /src/utils/wait-for-postgres.sh
