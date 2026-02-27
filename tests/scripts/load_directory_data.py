import requests

from tests.config.loader import DIRECTORY_SOURCES


def get_session(session_url):
    session = requests.Session()

    signin_mutation = '''
    mutation {
      signin(email: "admin", password: "admin") {
        status
        message
      }
    }
    '''
    response = session.post(session_url, json={'query': signin_mutation},
                            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Impossible to complete the test, authentication failed for EMX2 ')

    return session


def load_all_sources_test_data():
    for source in DIRECTORY_SOURCES:
        session = get_session(source['session_url'])
        query = 'mutation createSchema($name:String, $description:String, $template: String, $includeDemoData: Boolean){createSchema(name:$name, description:$description, template: $template, includeDemoData: $includeDemoData){message}}'
        variables = {
            "name": "ERIC",
            "description": None,
            "template": "BIOBANK_DIRECTORY",
            "includeDemoData": True
        }
        response = session.post(source['session_url'], json={'query': query, 'variables': variables})
        print(response.content)
        if response.status_code != 200:
            raise Exception(
                f'Impossible to load test Directory data for source "{source['session_url']}": {response.content}')


def main():
    print('Loading test directory data, this might take a while....')
    load_all_sources_test_data()


if __name__ == '__main__':
    main()