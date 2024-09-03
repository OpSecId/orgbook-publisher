FROM python:3.11-slim

WORKDIR /orgbook-publisher

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app ./app
COPY app config.py main.py ./

CMD [ "hypercorn", "-b", "0.0.0.0:8000", "main:app" ]