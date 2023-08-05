import os, imp, shelve

from yac.lib.config import get_config_path, get_lib_path
from yac.lib.registry import set_string_value, get_string_value, get_registry_keys


def get_fqdn(app, env, preffix="", suffix=""):

    return get_namer_module().get_fqdn(app, env, preffix, suffix)

def get_db_host_name(app, env, preffix="", suffix=""):

    return get_namer_module().get_db_host_name(app, env, preffix, suffix)

def get_stack_name(app, env, suffix=""):

    return get_namer_module().get_stack_name(app, env, suffix)

def get_cluster_name(app, env, suffix=""):

    return get_namer_module().get_cluster_name(app, env, suffix)   

def get_cname(app, env, suffix=""):

    return get_namer_module().get_cname(app, env, suffix)

def get_resource_name(app, env, resource, suffix=""):

    return get_namer_module().get_resource_name(app, env, resource, suffix)

def get_sg_name(app, env, resource, suffix=""):

    return get_namer_module().get_sg_name(app, env, resource, suffix)            

def get_host_name(app, env, suffix="" ):

    return get_namer_module().get_host_name(app, env, suffix)

def get_namer_module():

    return imp.load_source('yac.lib.naming',get_namer())

def get_namer():

    # load naming logic from local db
    yac_db_path = os.path.join( get_config_path(),'db','yac_db')

    yac_db = shelve.open(yac_db_path, 'c')

    yac_namer = yac_db.get('yac_namer')

    if not yac_namer:

        # load default namer
        yac_namer = os.path.join( get_lib_path(),'naming_default.py')

    return yac_namer

def get_all_naming_standard_keys():

    naming_standards = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if '-naming' in key:
            # remove the naming part
            naming_standards = naming_standards + [key.replace('-naming','')]

    return naming_standards

def get_namer_code_from_registry(namer_registry_key):

    namer_code = ""
    if namer_registry_key:

        # get namer logic from registry
        namer_code = get_string_value('%s-naming'%namer_registry_key)

    return namer_code

def set_namer(namer_registry_key):

    namer_code = get_namer_code_from_registry(namer_registry_key)

    if namer_code:

        # write namer code to file under lib
        namer_file_name = 'naming_%s.py'%namer_registry_key
        yac_namer_path = os.path.join( get_lib_path(),'customizations', namer_file_name)

        with open(yac_namer_path,'w') as yac_namer_path_fp:
           yac_namer_path_fp.write(namer_code)

        # save file with path to local yac_db
        yac_db_path = os.path.join( get_config_path(),'db','yac_db')

        yac_db = shelve.open(yac_db_path)

        yac_db['yac_namer'] = yac_namer_path

def clear_custom_namer():

    # save file with path to local yac_db
    yac_db_path = os.path.join( get_config_path(),'db','yac_db')

    yac_db = shelve.open(yac_db_path)

    yac_db['yac_namer'] = ""       

# register namer into yac registry
def register_namer(namer_registry_key, namer_path):

    with open(namer_path) as namer_path_fp:
        yac_namer = namer_path_fp.read()

        if yac_namer:

            # set the namer in the registry
            set_string_value('%s-naming'%namer_registry_key, yac_namer)


# TODO: do a global /s/get_naming_std/get_vpc_defs
# then delete this method
def get_naming_std():

    # load std from db

    if os.environ.get('YAC_NAMER'):

        guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

        return guest_namer.get_naming_std()

    else:

        return yac.lib.naming_default.get_naming_std()
