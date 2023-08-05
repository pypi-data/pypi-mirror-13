#!/usr/bin/env python

import os, sys, json, argparse, getpass, inspect
from sets import Set
import slib # for getting path
from yac.lib.stack import create_stack, stack_exists, get_stack_elements, get_stack_templates
from yac.lib.stack import get_template_variables, combine_stack_templates
from yac.lib.name import get_stack_name, get_cluster_name, get_fqdn, get_db_host_name
from slib.vpc import get_vpc_ids, get_subnet_ids, get_db_subnet_groups

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_exlusions(exlusions_arg):

    # use map to strip leading/trailing white spaces
    return map(str.strip,exlusions_arg.split(',')) if exlusions_arg else []
    

def are_exclusions_valid(parser, arg):

    # use map to strip leading/trailing white spaces
    exclusions = get_exlusions(arg)

    valid_stack_resources = get_stack_elements()
    # compare exclusions input to accepted stack elements. set formed via
    # intersection of accepted elements and exclusions should have same number of 
    # elents as exclusions
    if len(Set(valid_stack_resources) & Set(exclusions)) != len(exclusions):

        parser.error("One of the stack exlusions is invalid. Choose from %s" % (arg,str(valid_stack_resources)))
    else:
        return arg        

def get_conf_dir():

  # return the abs path to the config directory
  return os.path.join(os.path.dirname(inspect.getfile(slib)),'../config')

def load_user_params(stack_params, params_str):

    if params_str:

        user_params = json.loads(params_str)

        for key in user_params.keys():
            stack_params.append((str(key),user_params[key]))

    return stack_params

def main():

    parser = argparse.ArgumentParser('Print a stack for a YAC application via cloudformation')
    # required args
    parser.add_argument('app',  help='name of the app to build an stack for', 
                                choices=['jira','crowd','confluence','bamboo','hipchat'])
    parser.add_argument('env',  help='the env', 
                                choices=['dev', 'stage', 'prod','archive'])
    parser.add_argument('vpc',  help='the name (or partial name) of the VPC to build stack in')

    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    

    parser.add_argument('-x','--exclusions', help='exclude these stack elements. csv list with choices in [i-elb,e-elb,efs,rds,ecs]',
                                          type=lambda x: are_exclusions_valid(parser, x))
    parser.add_argument('-p','--params',  help='stack params overrides (formatted as json string)')
    parser.add_argument('-d','--dryrun',  help='dry run the stack change, printing template to stdout', 
                                          action='store_true')
    parser.add_argument('--suffix',  help='app name suffix (allows you to create multiple instances of the same app in the same env)',
                                     default='')      
    parser.add_argument('--appstack', help='path to the app-specific cloud formation template file for this app (useful to keep your stack configuration in scm)',
                                type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--desc', help='the description to put on the stack')
    parser.add_argument('--snapshot', help='if creating a new stack with a DB, create DB from this snapshot id',
                                     default='')    

    args = parser.parse_args()

    exclusions = get_exlusions(args.exclusions)

    # get stack name based on app and env
    stack_name = get_stack_name(args.app, args.env, args.suffix)

    # determine if we are building or updating this stack
    action = "Udating" if stack_exists(stack_name) else "Building"

    # get the templates to use based on the exclusions and argments
    templates_files = get_stack_templates(args.appstack, exclusions)

    # get the template variables for this stack
    template_variables = get_template_variables(args.app, args.env, args.desc)

    # combine the tempates into an complete stack template for the stack requested
    stack_template = combine_stack_templates(templates_files, template_variables)

    # pprint template dictionary to a string
    stack_template_str = json.dumps(stack_template,indent=4)

    # **************************** Print Time! ************************************
    user_msg = "%s stack %s"%(action,stack_name)

    if args.dryrun:

        # do a dry-run by printing the stack template and stack parameters to stdout
        print "stack template %s"%stack_template_str
        # print "stack parameters: %s"%stack_params
        print user_msg

    else:

        # send 'roger that' text to stdout in green text and give user chance to bail
        raw_input(user_msg + "\nHit <enter> to continue..." )


        print 'Stack %s in progress - use AWS console to watch construction and/or see errors'%action
        
