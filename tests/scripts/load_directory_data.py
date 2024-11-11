import requests

SESSION_URL = 'http://localhost:8080/api/graphql'

def get_session():
    session = requests.Session()

    signin_mutation = '''
    mutation {
      signin(email: "admin", password: "admin") {
        status
        message
      }
    }
    '''
    response = session.post(SESSION_URL, json={'query': signin_mutation},
                            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Impossible to complete the test, authentication failed for EMX2 ')

    return session


def load_all_directory_test_data():
    session = get_session()
    query = 'mutation createSchema($name:String, $description:String, $template: String, $includeDemoData: Boolean){createSchema(name:$name, description:$description, template: $template, includeDemoData: $includeDemoData){message}}'
    variables = {
        "name": "ERIC",
        "description": None,
        "template": "BIOBANK_DIRECTORY",
        "includeDemoData": True
    }
    response = session.post(SESSION_URL, json={'query': query, 'variables': variables})
    print(response.content)
    if response.status_code != 200:
        raise Exception(
            'Impossible to load test Directory data')


def main():
    print('Loading test directory data, this might take a while....')
    load_all_directory_test_data()


if __name__ == '__main__':
    main()