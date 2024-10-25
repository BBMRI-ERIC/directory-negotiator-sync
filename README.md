# directory-negotiator-sync

# directory-negotiator-sync
Service to synchronize ressources from the BBMRI-ERIC Directory into the BBMRI-ERIC Negotiator.
The service is composed of a main chron that periodically reads all the resource objects from the EMX-2 directory
and then checks if there are some resources to add or update. 
The service communicates with the Negotiator by client credentials authentication and authorization (Lifescience-AAI). 

This is a list of the attributes of Organization, Resource and Network that are checked and ipdated by the service
(in case of object already present in the negotiator): 

+ For Organization: Name attribute
+ For Resource: Name and Description attributes
+ For Network: Name, URL and Contact Email attributes

## Configuration parameters
This is a list of all the configuration parameters for the service: 



| Parameter Code | Parameter Description                                                                                   | 
|----------------|---------------------------------------------------------------------------------------------------------|
| DIRECTORY_EMX2_ENDPOINT | The endpoint of the Directory (EMX2 based) GraphQL API. This is used to read Directory's data.          |
| NEGOTIATOR_ENDPOINT| The endpoint of Negotiator's API, used to write data (add/update Organizations, Resources and Networks) |
| NEGOTIATOR_CLIENT_AUTH_CLIENT_ID | The client ID for authentication to the Negotiator                                                      |
| NEGOTIATOR_CLIENT_AUTH_CLIENT_SECRET | The client secret for authentication to the Negotiator                                                  |
| NEGOTIATOR_CLIENT_AUTH_OIDC_TOKEN_ENDPOINT | The endpoint of the Lifescience-AAI service authentication to the Negotiator (token request) |
| SYNC_JOB_SCHEDULE_INTERVAL | The interval (in seconds) of the Chron main service. The synchronization will be performed every [X] seconds according to this value |


