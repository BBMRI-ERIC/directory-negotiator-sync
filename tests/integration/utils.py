from typing import Literal

import pytest
from requests.auth import HTTPBasicAuth

from models.dto.network import NegotiatorNetworkDTO
from .conftest import DIRECTORY_API_URL, SESSION_URL


def add_or_update_biobank(biobank_id, biobank_pid, biobank_name, biobank_description, biobank_contact, biobank_url,
                          biobank_withdrawn, operation=Literal['insert', 'update']):
    session = pytest.directory_session
    query = f'mutation {operation}($value:[BiobanksInput]){{{operation}(Biobanks:$value){{message}}}}'
    variables = {
        "value": [
            {
                "withdrawn": biobank_withdrawn,
                "id": biobank_id,

                "pid": biobank_pid,
                "name": biobank_name,
                "description": biobank_description,
                "country": {
                    "name": "NL"
                },
                "contact": {
                    "id": biobank_contact,
                },
                "juridical_person": {
                    "id": "bbmri-eric:contactID:NL_person1",
                },
                "url": biobank_url,
                "national_node": {
                    "id": "NL",
                    "description": "Netherlands"
                },
                'services': [
                    {'id': 'bbmri-eric:serviceID:DE_1234'}
                ]
            }
        ]
    }

    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables},
                            auth=HTTPBasicAuth('admin', 'admin'))
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when adding the new biobank. Status code: {response.status_code} . Error: {response.text}')


def add_or_update_collection(collection_id, collection_name, collection_description, network, collection_contact,
                             collection_url, collection_withdrawn,
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
                    "name": "NL"
                },
                "contact": {
                    "id": collection_contact
                },
                'url': collection_url,
                'withdrawn': collection_withdrawn,
                "national_node": {
                    "id": "NL",
                    "description": "Netherlands"
                },
                "network": network,
                "biobank": {
                    'id': "bbmri-eric:ID:NL_biobank2"
                },
                "biobank_label": "Biobank2",
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
                    "id": "bbmri-eric:contactID:EU_network",
                },
                "national_node": {
                    "id": "NL",
                    "description": "Netherlands"
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
        {"id": "bbmri-eric:contactID:EU_network",
         "first_name": "EU",
         "last_name": "network Person",
         "title_after_name": "",
         "email": new_email_contact,
         "phone": "",
         "address": "",
         "zip": "",
         "country": {"name": "EU",
                     "label": "Europe"},
         "national_node": {"id": "EU",
                           "description": "European Union"}
         }
    ]
    }
    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            'Impossible to complete the test, error when updating email contact for person related to network')


def load_all_directory_test_data():
    session = pytest.directory_session
    query = 'mutation createSchema($name:String, $description:String, $template: String, $includeDemoData: Boolean){createSchema(name:$name, description:$description, template: $template, includeDemoData: $includeDemoData){message, taskId}}'
    variables = {
        "name": "ERIC",
        "description": None,
        "template": "BIOBANK_DIRECTORY",
        "includeDemoData": True
    }
    response = session.post(SESSION_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            'Impossible to load test Directory data')


def delete_all_directory_test_data():
    session = pytest.directory_session
    query = "mutation deleteSchema($id:String){deleteSchema(id:$id){message}}"
    variables = {"id": "ERIC"}
    response = session.post(SESSION_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            'Impossible to delete test Directory data')


def get_negotiator_network_id_by_external_id(external_id, negotiator_networks: [NegotiatorNetworkDTO]):
    for n in negotiator_networks:
        if n.externalId == external_id:
            return n.id


def add_or_update_service(service_id, service_name, service_description, operation=Literal['insert', 'update']):
    session = pytest.directory_session
    query = f'mutation {operation}($value:[ServicesInput]){{{operation}(Services:$value){{message}}}}'
    service = {
        'id': service_id,
        'name': service_name,
        'description': service_description,
        "serviceTypes": [
            {"name": "PET-Scans",
             "label": "PET Scans",
             "serviceCategory": {
                 "name": "imagingServices", "label": "Imaging Services"
             }
             }
        ],
        "accessDescription": "https://biobank2-service-access.nl",
        "national_node": {"id": "NL", "description": "Netherlands", "dns": "https://external_server.nl"},
    }
    variables = {
        "value": [service]
    }
    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables},
                            auth=HTTPBasicAuth('admin', 'admin'))
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when adding the new Service. Status code: {response.status_code} . Error: {response.text}')
