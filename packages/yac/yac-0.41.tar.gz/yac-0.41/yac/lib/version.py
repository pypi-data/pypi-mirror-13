import requests, jmespath

# for the registry find, find the latest version of the app input, in the container org input
def get_latest_version(app, container_org, registry_url='https://registry.hub.docker.com'):

    # endpoint use to determine the latest version in the registry input for this app
    endpoint_uri = "/v2/repositories/%s/%s/tags"%(container_org,app)

    # hit the endpoint
    endpoint_response = requests.get(registry_url + endpoint_uri) 

    # use jmespath to extract just the version value for each
    versions = jmespath.search("results[*].name",endpoint_response.json())

    # jmespath leaves a weird prefix on each result. remove by str conversion
    versions = [str(i) for i in versions]

    latest_version = ""

    if (versions and len(versions)>=1):

        if 'latest' in versions:

            latest_version = "latest"
        
        else:
            
            # sort and grab the last value in the resulting list (the latest version)
            versions.sort()
            latest_version = versions[-1]

    return str(latest_version)