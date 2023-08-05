import os
import yac.yaccli.lib.name_std

def get_stack_name(app, env, preffix="", suffix=""):

	return '%s.%s.%s'%(app,env,'brikit')

def get_naming_std(file_name):

	return {}	