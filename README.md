# directory-negotiator-sync

Service to synchronize resources from the BBMRI-ERIC Directory into the BBMRI-ERIC Negotiator.
The service is composed of a main chron that periodically reads all the resource objects from the EMX-2 directory
and then checks if there are some resources to add or update.
The service communicates with the Negotiator by client credentials authentication and authorization (Lifescience-AAI).

This is a list of the attributes of Organization, Resource and Network that are checked and updated by the service
(in case of object already present in the negotiator):

+ For Organization: Name, Description, Contact Email and Withdrawn attributes
+ For Resource: Name, Description, Contact Email and Withdrawn attributes
+ For Network: Name, Description and Contact Email attributes
+ For Services: Name, Description, Contact Email (they are added/updated as Resources)
+ For National Nodes: Name, Description and Contact Email attributes (they are added/updates as Networks in the
  Negotiator)

## Configuration parameters

The configuration parameters are set through the usage of a .yaml file (see a template under ./conf).
Notice that multiple directory sources are allowed, if needed. This is the list of the config parameters:

| Parameter Code                           | Parameter Description                                                                                                                                                                  | 
|------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| sources_endpoint.url                     | The endpoint of the Directory (EMX2 based) GraphQL API. This is used to read Directory's data, and it points to the Directory Schema                                                   |
| sources_endpoint.session_url             | The session url of the specific source. This is used to open the DB session needed to get data from the source                                                                         |
| sources_endpoint.priority                | The priority of the source. In case of presence of more than one source with the same entities (same ID) sync is performed taking the values from the source with highest priority (1) |
| negotiator_endpoint.url                  | The endpoint of Negotiator's API, used to write data (add/update Organizations, Resources and Networks)                                                                                |
| negotiator_endpoint.auth_client_id       | The client ID for authentication to the Negotiator                                                                                                                                     |
| negotiator_endpoint.auth_client_secret   | The client secret for authentication to the Negotiator                                                                                                                                 |
| negotiator_endpoint.auth_oidc_token_uri  | The endpoint of the Lifescience-AAI service authentication to the Negotiator (token request)                                                                                           |
| negotiator_endpoint.auth_oidc_ssl_verify | Boolean parameter to set for SSL verification of oidc service. Recommented to be set to true for production environments                                                               |
| sync_job_schedule_interval               | The interval (in seconds) of the Chron main service. The synchronization will be performed every [X] seconds according to this value                                                   |

## Multiple Directories support

Since version 1.3 multiple directories sync is supported. The service is able to read Directory data from multiple
endpoints, with a priority assigned to each of them. 1 is the highest priority, 2 the immediately lower and so on.
Priorities are mandatory and are needed to decide which is the master Directory for sync, in case of the same entities (same IDs) are present in more 
the one resource. For example, if the biobank with ID "test_bb" is present in source A having priority 1 and in source B having priority 2, the sync 
service will update this biobank taking the attribute values from source A, as it has the highest priority. 

## Integration tests

Prerequisite: a compose file to run negotiator, oidc test service and emx2 testing directory is available under
` negotiator_directory_sync/tests/compose `  .

First, from this directory run the compose:

`docker-compose -f docker-compose-integration-tests.yml  up -d`

Note: Adjust the build reference to the Negotiator accordingly before run.

Wait for a minute that all the services are up and running, then run the script that adds initial sample data into the test directories: 

From ` negotiator_directory_sync/tests/scripts ` run:

` python load_directory_data.py `

Wait for another minute, then run the integration tests in case of a single Directory: 
From ` negotiator_directory_sync/tests/integration ` run:

` pytest integration_tests_single_directory.py `

You can also run the integration test in case of multiple Directories: 

` pytest integration_tests_multiple_directories.py `


## Health endpoint 

An endpoint to check that the microservice is up and running is available on port 8088. The endpoint to call is:

` http://[YOUR_HOST]:8088/api/actuator/health `

In case of healthiness, a GET to the previous endpoint will return 200 with this response: 

` {"status":"UP"} `


## Security

This section describes the OIDC configuration required to enable REST communication between a Negotiator instance and this service. Typically, no security is required to read data from the source (BBMRI) directory because the related API is publicly available.
Negotiator's API, instead, are protected via oidc, so only the known clients can connect and perform operations
with the negotiator. This can be either set on a Negotiator's test instance (by setting up an own oidc server)
and on the Negotiator's production instance, that uses LifeScience AAI for security. 
The sync service uses Client Credentials to log into the Negotiator, an obtain a valid token to perform update 
operations on the various resources. So, a Client Id and a Client secret must be provided, together with the 
reference URL related to the oidc service to obtain the token. 
The environment variables used by the service (for versions >= 1.3.0) are:

 - AUTH_CLIENT_ID
 - AUTH_CLIENT_SECRET 
 - AUTH_OIDC_TOKEN_URI 
 - AUTH_OIDC_SSL_VERIFY

These are set through the yaml configuration file described above. The correspondent yaml variables are:

 - negotiator_endpoint.auth_client_id                                                                                                                                  |
 - negotiator_endpoint.auth_client_secret                                                                                                                              |
 - negotiator_endpoint.auth_oidc_token_uri
 - negotiator_endpoint.auth_oidc_ssl_verify

For example, suppose to set up a testing environment, similar to the one used by the integration tests, 
composed by a Negotiator test instance, an oidc test server and this sync service. The yaml configuration will be: 

```yaml
negotiator_endpoint:
    url: 'http://localhost:8081/api/v3'
    auth_client_id: '123'
    auth_client_secret: '123'
    auth_oidc_token_uri: 'http://localhost:4011/connect/token'
    auth_oidc_ssl_verify: false
```

In production, that's the same, only the values will change. It is strongly recommended to set ssl verification to true.

**WARNING**:
Keep the client ID and client secret information secret, and never publish them or provide them to anyone.

For version < 1.3.0 of the sync service, instead, the three parameters are provided as environment variables, for example in a Docker Compose file (these variables have been replaced by the YAML file in version >= 1.3.0).
This is a snippet of the sync service configuration in a Docker Compose file:

```yaml
version: '3.9'
  services:
    directory-negotiator-sync:
      [...]
      environment:
        - DIRECTORY_EMX2_ENDPOINT=https://directory-emx2-acc.molgenis.net/ERIC/directory/graphql
        - NEGOTIATOR_ENDPOINT=http://negotiator:8081/api/v3
        - NEGOTIATOR_CLIENT_AUTH_CLIENT_ID=123
        - NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET=123
        - NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT=http://localhost:4011/connect/token
        - SYNC_JOB_SCHEDULE_INTERVAL=20  
```

As you can see, the values of the three variables are the same, just the configuration changes

The auth.py module is the one that contains the methods to call the oidc service and get the token, given 
the above url and credentials. An automatic check of the token validity is performed, in a way to automatically 
refresh the token in case of expiration. 
