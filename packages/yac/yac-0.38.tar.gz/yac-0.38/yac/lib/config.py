import os

def get_config_path():

	config_path = os.path.join(os.path.dirname(__file__),'../','config')

	return config_path

def get_root_path():

	config_path = os.path.join(os.path.dirname(__file__),'../')

	return config_path