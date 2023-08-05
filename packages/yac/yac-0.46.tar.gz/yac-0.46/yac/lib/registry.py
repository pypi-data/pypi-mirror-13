import redis   # for remote registry
import shelve  # for local registry
import os
from yac.lib.config import get_config_path

# the url and port for the yac registry in redis
REGISTRY_URL = 'pub-redis-14705.us-east-1-3.4.ec2.garantiadata.com'
REGISTRY_PORT = 14705

def get_registry_keys():

    registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

    return registry.keys()

def set_remote_string_value(key_name, string_value):

    registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

    registry.set(key_name, string_value)    

def get_remote_string_value(key_name):

    registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

    return registry.get(key_name)

def delete_registry_value(key_name):

    registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

    return registry.delete(key_name)

def set_local_value(key_name, value):

    # save value to shelve db
    yac_db = _get_local_db()

    yac_db[key_name] = value

def get_local_value(key_name):  

    local_db = _get_local_db()

    if key_name in local_db:
        return local_db[key_name]
    else:
        return ""

def delete_local_value(key_name):   

    local_db = _get_local_db()

    if key_name in local_db:
        local_db.pop(key_name)
        

def _get_local_db():

    yac_db_path = os.path.join( get_config_path(),'db','yac_db')

    local_db = shelve.open(yac_db_path)

    return local_db