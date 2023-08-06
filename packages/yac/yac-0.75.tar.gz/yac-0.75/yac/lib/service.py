import os, json, jmespath
from sets import Set
from yac.lib.registry import get_registry_keys, get_remote_value, clear_entry_w_challenge
from yac.lib.registry import set_remote_string_w_challenge
from yac.lib.file import get_file_contents, register_file
from yac.lib.file_converter import find_and_convert_locals, find_and_delete_remotes
from yac.lib.variables import get_variable

REQUIRED_FIELDS=["sevice-name.value",
                "service-description.summary",
                "service-description.details",
                "service-description.maintainer.name",
                "service-description.maintainer.email",
                "CloudFormation"]

SUPPORTED_KEYS=["service-name",
                 "service-description",
                 "task-definition",
                 "resource-namer",
                 "files-for-boot",
                 "files-for-gold-image",
                 "restore-config",
                 "service-params",
                 "service-inputs",
                 "CloudFormation"]

YAC_SERVICE_SUFFIX="-service"

class ServiceError():
    def __init__(self, msg):
        self.msg = msg

def get_all_service_names():

    service_names = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if YAC_SERVICE_SUFFIX in key:
            # remove the suffix
            service_names = service_names + [key.replace(YAC_SERVICE_SUFFIX,'')]

    return service_names   

def get_service_by_name(service_name):

    service_descriptor = {}

    # first look in local registry
    if service_name:

        reg_key = service_name + YAC_SERVICE_SUFFIX

        # look in remote registry
        service_contents = get_remote_value(reg_key)

        if service_contents:

            # load into dictionary
            service_descriptor = json.loads(service_contents)

    return service_descriptor

def get_service_from_file(service_descriptor_file):

    service_descriptor = {}

    # pull the service descriptor from file
    with open(service_descriptor_file) as myservice_fp:

        service_descriptor = json.load(myservice_fp)

    # pull the service name out of the descriptor
    service_name = get_variable(service_descriptor, 'service-name')

    # set the servicefile path 
    servicefile_path = os.path.dirname(service_descriptor_file)

    return service_descriptor, service_name, servicefile_path


def clear_service(service_name, challenge):

    # if service is in fact registered
    service_descriptor = get_service_by_name(service_name)
    if service_descriptor:

        # clear service entry registry
        reg_key = service_name + YAC_SERVICE_SUFFIX
        clear_entry_w_challenge(reg_key, challenge)

        # clear any files referenced 
        find_and_delete_remotes(service_descriptor, challenge)      
    
    else:
        raise ServiceError("service with key %s doesn't exist"%service_name)

def validate_service(service_path):

    validation_errors = {}

    if os.path.exists(service_path):

        service_contents_str = get_file_contents(service_path)

        service_descriptor = json.loads(service_contents_str)

        missing_fields = find_missing_fields(service_descriptor)

        unsupported_keys = find_unsupported_keys(service_descriptor)
    
        if missing_fields:
            validation_errors["missing-fields"] = missing_fields
        if unsupported_keys:
            validation_errors["unsupported-keys"] = unsupported_keys

    return validation_errors

def find_unsupported_keys(service_descriptor):

    key_ustring_list = service_descriptor.keys()

    key_string_list = []
    # convert all keys from unicode to normal string
    for key_ustring in key_ustring_list:
        key_string_list = key_string_list + [str(key_ustring)]

    unsupported_keys = list( Set(key_string_list) - Set(SUPPORTED_KEYS))

    return unsupported_keys

# TODO. I tried to do this with with jmespath, which is way more elegant,
# but it doesn't seem to support hyphens in json keys. lame
def find_missing_fields(service_descriptor):

    missing_fields = []

    for i,field_path in enumerate(REQUIRED_FIELDS):

        path_parts = field_path.split(".")

        path_len = len(path_parts)

        if (path_len == 1 and 
            path_parts[0] not in service_descriptor):

            missing_fields = missing_fields + [REQUIRED_FIELDS[i]]
        
        elif (path_len == 2 and 
              path_parts[0] in service_descriptor and
              path_parts[1] not in service_descriptor[path_parts[0]]):

            missing_fields = missing_fields + [REQUIRED_FIELDS[i]]

        elif (path_len == 3 and 
              path_parts[0] in service_descriptor and
              path_parts[1] in service_descriptor[path_parts[0]] and 
              path_parts[2] not in service_descriptor[path_parts[0]][path_parts[1]]):

            missing_fields = missing_fields + [REQUIRED_FIELDS[i]]

    return missing_fields

# register service into yac registry
def register_service(service_name, service_path, challenge):

    if os.path.exists(service_path):

        service_contents_str = get_file_contents(service_path)

        if service_contents_str:

            reg_key = service_name + YAC_SERVICE_SUFFIX

            # get the base path of the service file
            servicefile_path = os.path.dirname(service_path)

            updated_service_contents_str = convert_local_files(service_name,
                                                  service_contents_str,
                                                  servicefile_path,
                                                  challenge)

            # set the service in the registry
            set_remote_string_w_challenge(reg_key, updated_service_contents_str, challenge)

    else:
        raise ServiceError("service path %s doesn't exist"%service_path)

# service_name formatted as:
#  <organization>/<service>:<version>
# service_path is path to the file container the service descriptor
def publish_service_description(service_name, service_path):

    print "implement me henry!"

# convert references to local files from relative paths to registry paths
def convert_local_files(service_name,service_contents_str,servicefile_path,challenge):

    # convert contents to json
    source_dict = json.loads(service_contents_str)

    source_dict_updated = find_and_convert_locals(source_dict, service_name, servicefile_path, challenge)

    # convert back to a string
    updated_service_str = json.dumps(source_dict_updated)

    return updated_service_str

def is_service_alias(service_alias, vpc_defs):

    is_alias = False

    # see if alias is a name in our vpc_defs alias dict
    if "aliases" in vpc_defs and service_alias in vpc_defs['aliases']:
        is_alias = True

    return is_alias

def get_alias_from_name(complete_service_name):

    alias = ""

    if complete_service_name:

        name_parts = complete_service_name.split(':')

        # see if first part can be further split
        name_prefix_parts = name_parts[0].split('/')

        # treat the alias as the last of the prefix parts
        alias = name_prefix_parts[-1]

    return alias

def get_service_name(service_alias, vpc_defs):

    server_name = ""
    # see if alias is a name in our vpc_defs alias dict
    if "aliases" in vpc_defs and service_alias in vpc_defs['aliases']:
        server_name = vpc_defs['aliases'][service_alias]

    return server_name 

# a service name is considered complete if it includes a version tag
def is_service_name_complete(service_name):

    is_complete = False

    name_parts = service_name.split(':')

    if len(name_parts)==2:

        # a tag is included, so name is complete
        is_complete = True

    return is_complete  

# if only know partial service name (no label), returns true
# if the complete version of the service is in registry
def is_service_available_partial_name(service_partial_name):

    is_available = False

    if not is_service_name_complete(service_partial_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_partial_name,"latest")
        service_desc = get_service_by_name(complete_name_candidate)

        if service_desc:
            is_available = True

    return is_available

def get_complete_name(service_name):

    complete_name = ""

    if not is_service_name_complete(service_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_name,"latest")
        service_desc = get_service_by_name(complete_name_candidate)

        if service_desc:
            complete_name = complete_name_candidate

    return complete_name