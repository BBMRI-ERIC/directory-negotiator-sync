FROM python:3.12-alpine3.20

RUN mkdir -p /opt/directory-negotiator-sync


COPY ./negotiator_directory_sync /opt/directory-negotiator-sync/negotiator_directory_sync
#COPY ./negotiator_directory_sync/auth /opt/directory-negotiator-sync/auth
#COPY ./negotiator_directory_sync/clients /opt/directory-negotiator-sync/clients
#COPY ./negotiator_directory_sync/exceptions /opt/directory-negotiator-sync/exceptions
#COPY ./negotiator_directory_sync/models /opt/directory-negotiator-sync/models
#COPY ./negotiator_directory_sync/synchronization /opt/directory-negotiator-sync/synchronization
#COPY ./negotiator_directory_sync/tests /opt/directory-negotiator-sync/tests
#COPY ./negotiator_directory_sync/utils /opt/directory-negotiator-sync/utils
COPY ./main.py /opt/directory-negotiator-sync/main.py
COPY ./requirements.txt /opt/directory-negotiator-sync/requirements.txt
COPY ./deploy/config.docker.yml /opt/directory-negotiator-sync/negotiator_directory_sync/conf/config.yml

WORKDIR /opt/directory-negotiator-sync

RUN pip install -r requirements.txt

#RUN export PYTHONPATH=$PYTHONPATH:/opt/directory-negotiator-sync/negotiator_directory_sync
ENV PYTHONPATH=/opt/directory-negotiator-sync


ENTRYPOINT ["python", "main.py"]





