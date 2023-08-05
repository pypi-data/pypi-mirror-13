#!/usr/bin/env python

import argparse, sys, json

from yac.lib.name import get_naming_std

def main():

	parser = argparse.ArgumentParser('Check naming standard configurations')

	# optional args
	parser.add_argument('-s', '--show',   help='show existing naming standards',
										  action='store_true')

	# pull out args
	args = parser.parse_args()

	if args.show:

		naming_std = get_naming_std()

		# pprint naming_std dictionary to a string
    	print json.dumps(naming_std,indent=4)

