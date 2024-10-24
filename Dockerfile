FROM python:3.12-alpine3.20

RUN mkdir -p /opt/directory-negotiator-sync

COPY ./negotiator_directory_sync /opt/directory-negotiator-sync/negotiator_directory_sync
COPY ./main.py /opt/directory-negotiator-sync/main.py
COPY ./requirements.txt /opt/directory-negotiator-sync/requirements.txt

WORKDIR /opt/directory-negotiator-sync

RUN pip install -r requirements.txt

#RUN export PYTHONPATH=$PYTHONPATH:/opt/directory-negotiator-sync/negotiator_directory_sync
ENV PYTHONPATH=/opt/directory-negotiator-sync

CMD ["python",  "main.py"]




