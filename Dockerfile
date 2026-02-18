FROM python:3.12-alpine3.20

RUN mkdir -p /opt/directory-negotiator-sync

COPY ./clients /opt/directory-negotiator-sync/clients
COPY ./models /opt/directory-negotiator-sync/models
COPY ./synchronization /opt/directory-negotiator-sync/synchronization
COPY ./tests /opt/directory-negotiator-sync/tests
COPY ./__init__.py /opt/directory-negotiator-sync/__init__.py
COPY ./auth.py /opt/directory-negotiator-sync/auth.py
COPY ./config.py /opt/directory-negotiator-sync/config.py
COPY ./exceptions.py /opt/directory-negotiator-sync/exceptions.py
COPY ./utils.py /opt/directory-negotiator-sync/utils.py
COPY ./main.py /opt/directory-negotiator-sync/main.py
COPY ./requirements.txt /opt/directory-negotiator-sync/requirements.txt

WORKDIR /opt/directory-negotiator-sync

RUN pip install -r requirements.txt

ENV PYTHONPATH=/opt/directory-negotiator-sync

CMD ["python",  "main.py"]




