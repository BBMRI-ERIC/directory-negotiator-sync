# directory-negotiator-sync

Service to synchronize resources from the BBMRI-ERIC Directory into the BBMRI-ERIC Negotiator.
The service is composed of a main chron that periodically reads all the resource objects from the EMX-2 directory
and then checks if there are some resources to add or update.
The service communicates with the Negotiator by client credentials authentication and authorization (Lifescience-AAI).

This is a list of the attributes of Organization, Resource and Network that are checked and ipdated by the service
(in case of object already present in the negotiator):

+ For Organization: Name, Description, Contact Email and Withdrawn attributes
+ For Resource: Name, Description, Contact Email and Withdrawn attributes
+ For Network: Name, Description and Contact Email attributes
+ For Services: Name, Description, Contact Email (they are added/updated as Resources)
+ For National Nodes: ame, Description and Contact Email attributes (they are added/updates as Networks in the
  Negotiator)

## Configuration parameters

The configuration parameters are set through the usage of a .yaml file (see a template under ./conf).
Notice that multiple directory sources are allowed, if needed. This is the list of the config parameters:

| Parameter Code                          | Parameter Description                                                                                                                                                                  | 
|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| sources_endpoint.url                    | The endpoint of the Directory (EMX2 based) GraphQL API. This is used to read Directory's data, and it points to the Directory Schema                                                   |
| sources_endpoint.session_url            | The session url of the specific source. This is used to open the DB session needed to get data from the source                                                                         |
| sources_endpoint.priority               | The priority of the source. In case of presence of more than one source with the same entities (same ID) sync is performed taking the values from the source with highest priority (1) |
| negotiator_endpoint.url                 | The endpoint of Negotiator's API, used to write data (add/update Organizations, Resources and Networks)                                                                                |
| negotiator_endpoint.auth_client_id      | The client ID for authentication to the Negotiator                                                                                                                                     |
| negotiator_endpoint.auth_client_secret  | The client secret for authentication to the Negotiator                                                                                                                                 |
| negotiator_endpoint.auth_oidc_token_uri | The endpoint of the Lifescience-AAI service authentication to the Negotiator (token request)                                                                                           |
| sync_job_schedule_interval              | The interval (in seconds) of the Chron main service. The synchronization will be performed every [X] seconds according to this value                                                   |

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

`docker-compose -f docker-compose-integation-tests.yml  up -d`

Note: Adjiust the build reference to the Negotiator accordingly before run.

Wait for a minute that all the services are up and running, then run the script that adds initial sample data into the test directories: 

From ` negotiator_directory_sync/tests/scripts ` run:

` python load_directory_data.py `

Wait for another minute, then rin the integration tests in case of a single Directory: 
From ` negotiator_directory_sync/tests/integration ` run:

` pytest integration_tests.py `

You can also run the integration test in case of multiple Directories: 

` pytest integration_tests_multiple_directories.py `





