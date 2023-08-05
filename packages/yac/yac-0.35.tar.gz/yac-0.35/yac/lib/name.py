import os, importlib
import yac.lib.name_std

def get_fqdn(app, env, preffix="", suffix=""):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_fqdn(app, env, preffix, suffix)

	else:

		return yac.lib.name_std.get_fqdn(app, env, preffix, suffix)

def get_db_host_name(app, env, preffix="", suffix=""):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_db_host_name(app, env, preffix, suffix)

	else:

		return yac.lib.name_std.get_db_host_name(app, env, preffix, suffix)

def get_stack_name(app, env, preffix="", suffix=""):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_stack_name(app, env, suffix)

	else:

		return yac.lib.name_std.get_stack_name(app, env, suffix)

def get_cluster_name(app, env, suffix=""):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_cluster_name(app, env, suffix)

	else:

		return yac.lib.name_std.get_cluster_name(app, env, suffix)		

def get_namer(app, env, preffix="", suffix=""):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_stack_name(app, env, preffix, suffix)

	else:

		return yac.lib.name_std.get_stack_name(app, env, preffix, suffix)

def get_naming_std(naming_std_file=os.environ.get('YAC_NAMING_STD')):

	if os.environ.get('YAC_NAMER'):

		guest_namer = importlib.import_module(os.environ.get('YAC_NAMER'))

		return guest_namer.get_naming_std(naming_std_file)

	else:

		return yac.lib.name_std.get_naming_std(naming_std_file)
