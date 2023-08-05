#!/usr/bin/env python
import time, os, json
from yac.lib.name import get_naming_std

def get_iam_role(iam_args, user_myapp_file=""):

	# precedence:
	# user-supplied via cli
	# user-supplied via myapp file
	# naming standards

	# if IAM role exists in the file provided by user, use that as
	# the role

	# default role is per naming standards
	iam_role = get_naming_std()['iam-role-default']

	if  iam_args:

		# override with role provided via cli arg
		iam_role = iam_args

	elif user_myapp_file:

		# see if an iam role is provided in a template Resources or ResourceTweaks 
		# block
		print 'TODO'

	return iam_role

