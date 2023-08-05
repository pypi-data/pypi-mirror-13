#!/usr/bin/env python

import argparse, inspect, os, json
import slib # for getting path to this module
from yac.lib.name import get_cluster_name, get_stack_name
# from yac.lib.cluster import create_or_update_cluster
# from yac.lib.taskdef import get_taskdefs_from_file, merge_app_specific_taskdefs, load_app_files

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


def main():

  parser = argparse.ArgumentParser(description='Build or update an ECS cluster for a YAC app')        

  # required args
  parser.add_argument('app',    help='name of the app to build ECS cluster for', 
                                choices=['jira','crowd','confluence','bamboo','hipchat'])
  parser.add_argument('env',    help='the environment to build ECS cluster for', 
                                choices=  ['dev','stage','prod','archive'])            
  parser.add_argument('--domain',  help='the top and second level domains for my apps (can also be set via name std file')
  parser.add_argument('--myapp',   help='path to an optional, app-specific, ECS task definition file (useful for keeping app config in scm)',
                                  type=lambda x: is_valid_file(parser, x))
  parser.add_argument('--naming', help='path to the naming standard file for this app (if you like to avoid env variables)',
                                  type=lambda x: is_valid_file(parser, x))
  parser.add_argument('-x','--suffix',  help='app suffix, to support multiple instances of the same app in the same env')
  parser.add_argument('-v','--variables',  help='additional taskdef template variables (formatted as json string)')

  parser.add_argument('-d','--dryrun',  help='dry run the task defintion creation by printing rendered template to stdout', 
                                        action='store_true')

  # pull out args
  args = parser.parse_args()
  env = args.env
  app = args.app
    

  raw_input("Creating cluster" + "\nHit <enter> to continue..." )