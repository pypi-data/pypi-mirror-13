#!/usr/bin/env python

import argparse, os, json

from yac.lib.security import get_iam_role

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('Check security configurations')

    parser.add_argument('--myapp', help='path to the app-specific cloud formation template file for this app (useful to keep your stack configuration in scm)',
                                type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--naming', help='path to the naming standard file for this app (if you like to avoid env variables)',
                                type=lambda x: is_valid_file(parser, x))

    # pull out args
    args = parser.parse_args()

    # first get IAM role
    iam_role = get_iam_role(iam_args="",user_myapp_file=args.naming)

    print 'Configured Security Setpoints'
    print 'Credentials File: %s'%os.path.exists('~/.aws/credentials')
    print 'IAM Role: %s'%iam_role['value']
    print 'SSL Cert: %s'%'TBD'
    print 'Key Pair: %s'%'TBD'
    
 