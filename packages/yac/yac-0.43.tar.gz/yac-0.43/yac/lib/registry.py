import redis

# the url and port for the yac registry in redis
REGISTRY_URL = 'pub-redis-14705.us-east-1-3.4.ec2.garantiadata.com'
REGISTRY_PORT = 14705

def get_registry_keys():

	registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.keys()

def set_string_value(key_name, string_value):

	registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

	registry.set(key_name, string_value)	

def get_string_value(key_name):

	registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.get(key_name)

def delete_registry_value(key_name):

	registry = redis.Redis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.delete(key_name)	
