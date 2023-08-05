#!/usr/bin/env python

import argparse, inspect, os, json
import slib # for getting path to this module
from yac.lib.name import get_cluster_name, get_cname, get_stack_name
from yac.lib.cluster import create_or_update_cluster
from yac.lib.taskdef import get_taskdefs_from_file, merge_app_specific_taskdefs, load_app_files

def get_env_param(env,suffix):

    if suffix:
        env_param = '%s/%s'%(suffix,env)
    else:
        env_param = env

    return env_param

def get_conf_dir():

    # return the abs path to the config directory
    return os.path.join(os.path.dirname(inspect.getfile(slib)),'../config')

def load_user_variables(taskdef_template_vars, variables_str):

    if variables_str:

        user_variables = json.loads(variables_str)

        taskdef_template_vars.update(user_variables.copy())

    return taskdef_template_vars


parser = argparse.ArgumentParser(description='Build or update an ECS cluster for a YAC app')        

# required args
parser.add_argument('app',    help='name of the app to build ECS cluster for', 
                              choices=['jira','crowd','confluence','bamboo','hipchat'])
parser.add_argument('env',    help='the environment to build ECS cluster for', 
                              choices=  ['dev','stage','prod','archive'])            
parser.add_argument('--domain',  help='the top and second level domains for my apps (can also be set via name std file')
parser.add_argument('-p','--path',    help='path to an optional, app-specific, ECS task definition file (useful for keeping app config in scm)')
parser.add_argument('-x','--suffix',  help='app suffix, to support multiple instances of the same app in the same env')
parser.add_argument('-v','--variables',  help='additional taskdef template variables (formatted as json string)')

parser.add_argument('-d','--dryrun',  help='dry run the task defintion creation by printing rendered template to stdout', 
                                      action='store_true')

# pull out args
args = parser.parse_args()
env = args.env
app = args.app
   
# variables that may need to be rendered into task definition templates for 
# standard SETS apps
taskdef_template_vars = {"app": app, 
                         "app_title": app.title(), 
                         "env": get_env_param(env,args.suffix),
                         "cname": get_cname(app,env)}

# load any additional template variables provided by user in args
taskdef_template_vars = load_user_variables(taskdef_template_vars, args.variables)

if args.nonstandard:

    # This is a standard app, so load standard-taskdef task definition 
    # dictionary used for all standard SETS apps
    # Pass template variables to render into the standard template
    standard_taskdef_file = os.path.join(get_conf_dir(),'standard-taskdef.json')
    app_taskdefs = get_taskdefs_from_file(standard_taskdef_file, 
                                          taskdef_template_vars)
else:
    # this is a non-standard app, so skip the standard task definitions
    app_taskdefs = {}

# load the (optional) app-specific dictionary provided for this app instance
if args.path:

  app_specific_taskdefs = get_taskdefs_from_file(args.path,
                                        taskdef_template_vars)
  # merge dictionaries
  app_taskdefs = merge_app_specific_taskdefs(app_taskdefs,app_specific_taskdefs)

  # load any files defined in the app-specific task definitions
  load_app_files(app_specific_taskdefs, taskdef_template_vars)

# get cluster name
cluster_name = get_cluster_name(app, env, args.suffix)

# get the stack name
stack_name = get_stack_name(app,env, args.suffix)

if args.dryrun:

    # do a dry-run of cluster change

    # send 'roger that' text to stdout in green text 
    print "%sDry run for cluster named %s for the %s app in the %s env%s"%('\033[92m',cluster_name,app,env,'\033[0m')

    create_or_update_cluster(cluster_name     = cluster_name, 
                             task_definitions = app_taskdefs,
                             dry_run          = True)

else:

    # do a for-reals cluster change

    # send 'roger that' text to stdout in green text 
    print "%sBuilding or updating cluster named %s for the %s app in the %s env%s"%('\033[92m',cluster_name,app,env,'\033[0m')

    create_or_update_cluster(cluster_name = cluster_name, 
                             task_definitions = app_taskdefs)

    print 'Cluster create or update is complete. ECS stack agents running on the %s stack should respond to the changes shortly.'%stack_name
    
