from typing import Literal

import pytest
from requests.auth import HTTPBasicAuth

from conftest import DIRECTORY_API_URL


def add_or_update_biobank(biobank_id, biobank_pid, biobank_name, biobank_description,
                          operation=Literal['insert', 'update']):
    session = pytest.directory_session
    query = f'mutation {operation}($value:[BiobanksInput]){{{operation}(Biobanks:$value){{message}}}}'
    variables = {
        "value": [
            {
                "withdrawn": "false",
                "id": biobank_id,

                "pid": biobank_pid,
                "name": biobank_name,
                "description": biobank_description,
                "country": {
                    "name": "CY"
                },
                "contact": {
                    "id": "bbmri-eric:contactID:AT_MUG_0001",
                },
                "national_node": {
                    "id": "AT",
                    "description": "Austria"
                }
            }
        ]
    }

    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables},
                            auth=HTTPBasicAuth('admin', 'admin'))
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when adding the new biobank. Status code: {response.status_code} . Error: {response.text}')


def add_or_update_collection(collection_id, collection_name, collection_description,
                             operation=Literal['insert', 'update']):
    session = pytest.directory_session
    query = f'mutation {operation}($value:[CollectionsInput]){{{operation}(Collections:$value){{message}}}}'
    variables = {
        "value": [
            {
                "id": collection_id,
                "name": collection_name,
                "description": collection_description,
                "country": {
                    "name": "CY"
                },
                "contact": {
                    "id": "bbmri-eric:contactID:AT_MUG_0001",
                },
                "national_node": {
                    "id": "AT",
                    "description": "Austria"
                },
                "biobank": {
                    'id': "bbmri-eric:ID:CY_ALLBIO"
                },
                "biobank_label": "ALLBIO INTERNATIONAL",
                "type": {
                    "name": "OTHER"
                },
                "order_of_magnitude": {
                    "name": 0
                },
                "order_of_magnitude_donors": {
                    "label": "10 - 100"
                },
                "data_categories":
                    {
                        "name": "OTHER"
                    },

            }
        ]
    }

    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables},
                            auth=HTTPBasicAuth('admin', 'admin'))
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when adding the new collection. Status code: {response.status_code} . Error: {response.text}')


def add_or_update_network(network_id, network_name, network_description, network_url, contact_id,
                          operation=Literal['insert', 'update']):
    session = pytest.directory_session
    query = f'mutation {operation}($value:[NetworksInput]){{{operation}(Networks:$value){{message}}}}'
    variables = {
        "value": [
            {
                "id": network_id,
                "name": network_name,
                "description": network_description,
                "contact": {
                    "id": "bbmri-eric:contactID:AT_MUG_0001",
                },
                "national_node": {
                    "id": "AT",
                    "description": "Austria"
                },
                "url": network_url,
                "contact": {
                    "id": contact_id
                },
            }
        ]
    }

    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables},
                            auth=HTTPBasicAuth('admin', 'admin'))
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when adding the new Network. Status code: {response.status_code} . Error: {response.text}')


def delete_object_from_directory(object_id, objects_input_type=Literal['Biobanks', 'Collections', 'Networks']):
    session = pytest.directory_session
    query = f'mutation delete($pkey:[{objects_input_type}Input]){{delete({objects_input_type}:$pkey){{message}}}}'
    variables = {'pkey': [{'id': object_id}]}
    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when delting the new {objects_input_type[:-1]}. Status code: {response.status_code} . Error: {response.text}')


def update_person_email_contact(new_email_contact):
    session = pytest.directory_session
    query = 'mutation update($value:[PersonsInput]){update(Persons:$value){message}}'
    variables = {"value": [
        {"id": "bbmri-eric:contactID:AT_MUG_0001",
         "first_name": "Sabrina",
         "last_name": "Kral",
         "title_after_name": "MSc",
         "email": new_email_contact,
         "phone": "+4331638572721",
         "address": "ZWT Neue Stiftingtalstraße 2B",
         "zip": "8010", "city": "Graz",
         "country": {"name": "AT",
                     "label": "Austria"},
         "national_node": {"id": "AT",
                           "description": "Austria"}
         }
    ]
    }
    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            'Impossible to complete the test, error when updating email contact for person related to network')
