import redis

# the url and port for the yac registry in redis
REGISTRY_URL = 'pub-redis-14705.us-east-1-3.4.ec2.garantiadata.com'
REGISTRY_PORT = 14705

def get_registry_keys():

	registry = redis.StrictRedis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.keys()

def set_string_value(key_name, string_value):

	registry = redis.StrictRedis(host=REGISTRY_URL, port=REGISTRY_PORT)

	registry.set(key_name, string_value)

def set_dictionary_value(key_name, dictionary_value):

	registry = redis.StrictRedis(host=REGISTRY_URL, port=REGISTRY_PORT)

	registry.hmset(key_name, dictionary_value)	

def get_string_value(key_name):

	registry = redis.StrictRedis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.get(key_name)

def get_dictionary_value(key_name):

	registry = redis.StrictRedis(host=REGISTRY_URL, port=REGISTRY_PORT)

	return registry.hgetall(key_name)	
