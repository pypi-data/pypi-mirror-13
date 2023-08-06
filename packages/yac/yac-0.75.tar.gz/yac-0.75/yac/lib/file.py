import os
from yac.lib.registry import set_remote_string_w_challenge, get_remote_value, get_registry_keys
from yac.lib.registry import clear_entry_w_challenge
from yac.lib.registry import set_local_value, get_local_value, delete_local_value, get_local_keys
from yac.lib.paths import get_yac_path


YAC_FILE_PREFIX="yac://"

class FileError():
    def __init__(self, msg):
        self.msg = msg


def get_all_file_keys():

    file_keys = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if file_in_registry(key):
            # remove the naming part
            file_keys = file_keys + [key.replace(YAC_FILE_PREFIX,'')]

    return file_keys    

def get_file_from_registry(file_key):

    file_contents = ""

    reg_key = get_file_reg_key(file_key)

    # get file from registry
    file_contents = get_remote_value(reg_key)

    return file_contents

def clear_file_from_registry(file_path, challenge):

    # if file is in fact registered
    if get_file_from_registry(file_path):

        # clear file entry
        reg_key = get_file_reg_key(file_path)

        clear_entry_w_challenge(reg_key, challenge)      
    
    else:
        raise FileError("file with key %s doesn't exist"%file_path)

# register file into yac registry
def register_file(file_key, file_path, challenge):

    if os.path.exists(file_path):

        with open(file_path) as file_path_fp:

            file_contents = file_path_fp.read()

            reg_key = get_file_reg_key(file_key)

            # set the file in the registry
            set_remote_string_w_challenge(reg_key, file_contents, challenge)

    else:
        raise FileError("file at %s doesn't exist"%file_path)

def get_file_reg_key(file_key):

    # add prefix to make it easy to identify files in the registry 
    return YAC_FILE_PREFIX + file_key

def get_file_contents(file_key_or_path, servicefile_path=""):
    
    file_contents = ""

    # if file is in registry
    if file_in_registry(file_key_or_path):
        file_contents = get_remote_value(file_key_or_path)

    # if file exists locally
    elif os.path.exists(file_key_or_path):
        with open(file_key_or_path) as file_arg_fp:
            file_contents = file_arg_fp.read()

    # if file exists relative to the service descriptor
    elif os.path.exists(os.path.join(servicefile_path,file_key_or_path)):
        with open(os.path.join(servicefile_path,file_key_or_path)) as file_arg_fp:
            file_contents = file_arg_fp.read()

    return file_contents

# a file is in the registry if the key includes the yac file prefix
def file_in_registry(file_key):
    return YAC_FILE_PREFIX in file_key

# a file is in yac sources if it exists in yac sources
def file_in_yac_sources(file_key):

    sources_root = get_yac_path()

    source_path = os.path.join(sources_root,file_key) 

    return os.path.exists(source_path)       
  