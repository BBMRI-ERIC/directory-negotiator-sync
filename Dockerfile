FROM python:3.12-alpine3.20

RUN mkdir -p /opt/directory-negotiator-sync

COPY ./negotiator_directory_sync /opt/directory-negotiator-sync/negotiator_directory_sync
COPY ./main.py /opt/directory-negotiator-sync/main.py
COPY ./requirements.txt /opt/directory-negotiator-sync/requirements.txt

WORKDIR /opt/directory-negotiator-sync

RUN pip install -r requirements.txt

#RUN export PYTHONPATH=$PYTHONPATH:/opt/directory-negotiator-sync/negotiator_directory_sync
ENV PYTHONPATH=/opt/directory-negotiator-sync
ARG DIRECTORY_EMX2_ENDPOINT
ARG NEGOTIATOR_ENDPOINT
ARG NEGOTIATOR_CLIENT_AUTH_CLIENT_ID
ARG NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET
ARG NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT
ARG SYNC_JOB_SCHEDULE_INTERVAL


ENTRYPOINT ["sh", "-c", "python main.py --directory_emx2_endpoint $DIRECTORY_EMX2_ENDPOINT --negotiator_endpoint $NEGOTIATOR_ENDPOINT --negotiator_client_auth_client_id $NEGOTIATOR_CLIENT_AUTH_CLIENT_ID --negotiator_client_auth_client_secret $NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET --negotiator_client_auth_oidc_token_endpoint $NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT --sync_job_schedule_interval $SYNC_JOB_SCHEDULE_INTERVAL"]





