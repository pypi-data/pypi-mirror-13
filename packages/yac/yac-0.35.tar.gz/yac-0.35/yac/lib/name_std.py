#!/usr/bin/env python
import time, os, json
from yac.lib.config import get_config_path

def get_stack_name(app, env, suffix=""):

    naming_std = get_naming_std()    

    # stack name for YAC stacks are per the following convention:
    # "<preffix>-<app>-<suffix>-<env>"
    name_parts = [naming_std['prefix']['value'], app, suffix, env]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    stack_name = naming_std['delimitter']['value'].join(name_parts)

    if naming_std['camelcase']:
        stack_name = stack_name.title()

    return stack_name

def get_cluster_name(app, env, preffix="", suffix=""):

    # cluster name for YAC stacks should match cluster names
    return get_stack_name(app, env, preffix, suffix)

# get cname for this env
def get_cname(app, env):    

    # CNames for our stacks are per the following convention:
    # lower: "<app><env>"
    # prod:  "<app>"
    # For example, for jira in the dev env, the name would be
    # "jiradev"
    # for jira in the production env, the cname would be 
    # "jira"

    if env=='dev':
        cname = '%s%s%s'%(app.lower(),env.lower(),'aws')
    elif env=='stage':
        cname='%s%s%s'%(app.lower(),'test','aws')
    elif env=='archive':
        cname='%s%s'%(app.lower(),'archive')        
    else:
        cname='%s%s'%(app.lower(),'aws')

    return cname

# get cname for this env
def get_fqdn(app, env, company, domain):

    return '%s.%s.%s'%(get_cname(app,env),company,domain)

# get the name of the db to be used with the app input
def get_db_name(app):    

    # DB names for our stacks are the same as the app name, all
    # lower case
    db_name = app.lower()

    return db_name

def get_resource_name(app, env, suffix, resource):

    naming_std = get_naming_std()    

    name_parts = [ app, suffix, env, resource]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = naming_std['delimitter']['value'].join(name_parts)

    return resource_name.title() if naming_std['camelcase'] else resource_name

def get_db_host_name(app,env, suffix=""):
    
    # DB host names for our stacks are per the following convention:
    # lower: "<app>-<suffix>-<env>-<creation timestamp in sec>"
    # For example, for jira in the dev env, if the db was created on
    # 11/17/2015 at 5:37 am, the name would be
    # jira-dev-1447767457
    # Including the date makes it easier to restore from snapshots

    naming_std = get_naming_std()

    if suffix:
        name = naming_std['delimitter'].join([app.lower(),suffix.lower(),env.lower(),str(int(time.time()))])
    else:
        name = naming_std['delimitter'].join([app.lower(),env.lower(),str(int(time.time()))])

    return name 
   
# get name of the db user to be used with the app input
def get_db_user_name(app):    

    # DB user/role for our stacks are the same as the app name, all
    # lower case
    db_user = app.lower()

    return db_user 

# get naming standards for your yac resourcs
def get_naming_std(naming_std_file=os.environ.get('YAC_NAMING_STD')):

    if (naming_std_file and os.path.exists(naming_std_file)):

        with open(os.environ.get('YAC_NAMING_STD')) as naming_std_file:
            naming_std = json.load(naming_std_file)

            # do a quick validation check
            if not ('vpc_name_tag' in naming_std and
                    'delimitter'   in naming_std and
                    'camelcase'    in naming_std and
                    'subnets'      in naming_std and
                    'e-elb' in naming_std['subnets'] and
                    'asg'   in naming_std['subnets'] and
                    'i-elb' in naming_std['subnets'] and
                    'efs'   in naming_std['subnets'] and
                    'rds'   in naming_std['subnets']):

                naming_std['valid']=False
                print 'Yac naming standard file incomplete. Please run "yac vpc -h" for assistence'
            else:
                naming_std['valid']=True

    else:
        # use the default naming standard
        with open(os.path.join( get_config_path(),'yac-naming-std.json')) as naming_std_file:
            naming_std = json.load(naming_std_file)
            naming_std['valid']=True
                            
    return naming_std