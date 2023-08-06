import os
from yac.lib.file import register_file, get_file_reg_key, file_in_registry
from yac.lib.registry import clear_entry_w_challenge

# convert references to local files in the source dictionary, and register
# each source file

def find_and_convert_locals(source_dict, service_key, servicefile_path, challenge):

    for key in source_dict.keys():

        if type(source_dict[key])==dict:
            source_dict[key] = find_and_convert_locals(source_dict[key],service_key,servicefile_path,challenge)

        elif type(source_dict[key])==list:
            source_dict[key] = find_and_convert_locals_list(source_dict[key],service_key,servicefile_path,challenge)

        else:
            source_dict[key] = find_and_convert_locals_leaf(source_dict[key],service_key, servicefile_path,challenge)

    return source_dict 

def find_and_convert_locals_list(source_list, service_key, servicefile_path, challenge):

    for i, item in enumerate(source_list):
        if type(item)==dict:
            source_list[i] = find_and_convert_locals(item, service_key, servicefile_path, challenge)           
        elif type(item)==list:
            source_list[i] = find_and_convert_locals_list(item, service_key, servicefile_path, challenge) 
        else:
            source_list[i] = find_and_convert_locals_leaf(item, service_key, servicefile_path,challenge)

    return source_list

def find_and_convert_locals_leaf(dict_leaf, service_key, servicefile_path, challenge):

    # see if the value is a file, and see if file is referenced relative to the 
    # service file
    if ( os.path.exists(os.path.join(servicefile_path,str(dict_leaf))) and
         os.path.isfile(os.path.join(servicefile_path,str(dict_leaf))) and
         not os.path.isabs(str(dict_leaf)) ):

        file_path = os.path.join(servicefile_path,str(dict_leaf))

        # prefix file path with service key to avoid naming collisions
        file_key = os.path.join(service_key,str(dict_leaf))

        register_file(file_key, file_path, challenge)

        file_url = get_file_reg_key(file_key)

        return file_url

    else:

        return dict_leaf

def find_and_delete_remotes(source_dict, challenge):

    for key in source_dict.keys():

        if type(source_dict[key])==dict:
            source_dict[key] = find_and_delete_remotes(source_dict[key],challenge)

        elif type(source_dict[key])==list:
            source_dict[key] = find_and_delete_remotes_list(source_dict[key], challenge)

        else:
            source_dict[key] = find_and_delete_remotes_leaf(source_dict[key],challenge)

    return source_dict 
              
def find_and_delete_remotes_list(source_list, challenge):

    for i, item in enumerate(source_list):
        if type(item)==dict:
            source_list[i] = find_and_delete_remotes(item, challenge)           
        elif type(item)==list:
            source_list[i] = find_and_delete_remotes_list(item, challenge) 
        else:
            source_list[i] = find_and_delete_remotes_leaf(item, challenge)

    return source_list

def find_and_delete_remotes_leaf(item, challenge):

    # see if the value is a file
    if file_in_registry(str(source_dict[key])):

        clear_entry_w_challenge(str(source_dict[key]), challenge)
        