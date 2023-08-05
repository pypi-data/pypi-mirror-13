#!/usr/bin/env python
import time, os, json
from yac.lib.config import get_config_path

def get_stack_name(app, env, suffix=""):

    naming_std = get_naming_std()    

    name_parts = [naming_std['prefix']['value'], app, suffix, env]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    stack_name = naming_std['delimitter']['value'].join(name_parts)

    return stack_name.title() if naming_std['camelcase']['value'] else stack_name

def get_cluster_name(app, env, suffix=""):

    # cluster name for YAC stacks should match cluster names
    return get_stack_name(app, env, suffix)

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

# each EC2 instance in the ASG will get this host name
def get_host_name( app, env, suffix=""):

    naming_std = get_naming_std()    

    name_parts = [ app, suffix, env ]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = naming_std['delimitter']['value'].join(name_parts)

    return resource_name.title() if naming_std['camelcase']['value'] else resource_name

# get cname for this env
def get_fqdn(app, env, company, domain):

    return '%s.%s.%s'%(get_cname(app,env),company,domain)

# get the name of the db to be used with the app input
def get_db_name(app):    

    # DB names for our stacks are the same as the app name, all
    # lower case
    db_name = app.lower()

    return db_name

# name each yac resource
def get_resource_name(app, env, resource, suffix=""):

    naming_std = get_naming_std()    

    # if the resource is a db, add a timestamp to the end (including
    # the timestamp makes it easier to restore from snapshots)
    if resource=='rds':
        name_parts = [ app, suffix, env ]
        name_parts = name_parts + [str(int(time.time()))]
    else:
        name_parts = [ app, suffix, env, resource]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = naming_std['delimitter']['value'].join(name_parts)

    return resource_name.title() if naming_std['camelcase']['value'] else resource_name

# each yac resource has a matching security group, named per this fxn
def get_sg_name(app, env, resource, suffix=""):

    naming_std = get_naming_std()

    name_parts = [ app, suffix, env, resource, 'sg']

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = naming_std['delimitter']['value'].join(name_parts)

    return resource_name.title() if naming_std['camelcase']['value'] else resource_name    
   
# get name of the db user to be used with the app input
def get_db_user_name(app):    

    # DB user/role for our stacks are the same as the app name, all
    # lower case
    db_user = app.lower()

    return db_user 

# get naming standards for your yac resourcs
def get_naming_std():

    naming_std_file=os.environ.get('YAC_NAMING_STD')

    if (naming_std_file and os.path.exists(naming_std_file)):

        with open(os.environ.get('YAC_NAMING_STD')) as naming_std_file:
            naming_std = json.load(naming_std_file)

            # do a quick validation check
            if False:

                naming_std['valid']=False
                print 'Yac naming standard file incomplete. Please run "yac naming -h" for assistence'
            else:
                naming_std['valid']=True

    else:
        # use the default naming standard
        with open(os.path.join( get_config_path(),'yac-naming-std.json')) as naming_std_file:
            naming_std = json.load(naming_std_file)
            naming_std['valid']=True
                            
    return naming_std