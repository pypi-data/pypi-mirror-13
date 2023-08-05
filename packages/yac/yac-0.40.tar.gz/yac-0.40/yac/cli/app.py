#!/usr/bin/env python

import argparse, inspect, os, json, sys
from yac.lib.name import get_cluster_name, get_stack_name, get_cname
from yac.lib.app import get_template_variables, get_app_templates, combine_app_templates, upload_app_files
from yac.lib.app import get_user_count, create_or_update_cluster

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser(description='Build or update an ECS cluster for a YAC app')        

    # required args
    parser.add_argument('app',    help='name of the app to build ECS cluster for', 
                                  choices=['jira','crowd','confluence','bamboo','hipchat'])
    parser.add_argument('env',    help='the environment to build ECS cluster for', 
                                  choices=  ['dev','stage','prod','archive'])            
    parser.add_argument('-d',
                        '--dryrun',  help='dry run the task defintion creation by printing rendered template to stdout', 
                                     action='store_true')
    parser.add_argument('--myapp',   help='path to an optional, app-specific, ECS task definition file (useful for keeping app config in scm)',
                                     type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--users',   help='the number of users the app will be licensed to support',
                                     choices=["25","50","100","250","500","2000","10000","10000+"],
                                     default= "50")
    parser.add_argument('--suffix',  help='app suffix, to support multiple instances of the same app in the same env')

    # pull out args
    args = parser.parse_args()

    # get the user count
    user_count = get_user_count(args.myapp, args.users) 

    # get the template variables for this app and env
    template_variables = get_template_variables(args.app, args.env, args.suffix, user_count)

    # get the templates to use
    templates_files = get_app_templates(args.myapp)

    # combine the templates and render variables to form a complete app template for the app requested
    app_template = combine_app_templates(templates_files, template_variables)  

    # get cluster name
    cluster_name = get_cluster_name(args.app, args.env, args.suffix)

    if args.dryrun:

        # do a dry-run by printing the app template
        app_template_str = json.dumps(app_template,indent=2)

        print "app template %s"%app_template_str

        # send 'roger that' text to stdout in green text 
        print "%sDry run for ECS cluster named %s for the %s app in the %s env, tuned to support up to %s users%s"%('\033[92m',cluster_name,args.app,args.env,user_count,'\033[0m')
        print "%sSanity check the template above.%s"%('\033[92m','\033[0m')

    else:

        print "%sCreating ECS cluster named %s for the %s app in the %s env, tuned to support up to %s users%s"%('\033[92m',cluster_name,args.app,args.env,user_count,'\033[0m')
        raw_input("Hit <enter> to continue..." )

        # upload configurations files required by the containers
        upload_app_files(app_template, template_variables)

        create_or_update_cluster(cluster_name     = cluster_name, 
                                 task_definitions = app_template)