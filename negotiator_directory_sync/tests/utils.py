import pytest
from requests.auth import HTTPBasicAuth

DIRECTORY_API_URL = "http://localhost:8080/Directory/directory/graphql"


def add_new_biobank_to_directory(biobank_id, biobank_pid, biobank_name, biobank_description):
    session = pytest.directory_session
    query = "mutation insert($value:[BiobanksInput]){insert(Biobanks:$value){message}}"
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


def delete_biobank_from_directory(biobank_id):
    session = pytest.directory_session
    query = 'mutation delete($pkey:[BiobanksInput]){delete(Biobanks:$pkey){message}}'
    variables = {'pkey': [{'id': biobank_id}]}
    response = session.post(DIRECTORY_API_URL, json={'query': query, 'variables': variables})
    if response.status_code != 200:
        raise Exception(
            f'Impossible to complete the test, erroor when delting the new biobank. Status code: {response.status_code} . Error: {response.text}')
