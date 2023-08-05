#!/usr/bin/env python
import time, os, json
from yac.lib.config import get_config_path
from yac.lib.vpc import get_vpc_defs

def get_stack_name(app, env, suffix=""):

    vpc_defs = get_vpc_defs()    

    name_parts = [vpc_defs['prefix']['value'], app, suffix, env]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    stack_name = vpc_defs['delimitter']['value'].join(name_parts)

    return stack_name.title() if vpc_defs['camelcase']['value'] else stack_name

def get_cluster_name(app, env, suffix=""):

    # Cluster name has cost center convolved in such that clusters can be connected to 
    # teams. When and if aws add support for cluster tags (like most other aws resources),
    # then we can remove cost center from the name
    vpc_defs = get_vpc_defs()    

    name_parts = [vpc_defs['cost_center']['value'],vpc_defs['prefix']['value'], app, suffix, env]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    stack_name = vpc_defs['delimitter']['value'].join(name_parts)

    return stack_name.title() if vpc_defs['camelcase']['value'] else stack_name

    # cluster name for YAC stacks should match cluster names
    return get_stack_name(app, env, suffix)

# get cname for this env
def get_cname(app, env, suffix=""):    

    # CNames for our stacks are per the following convention:
    # lower: "<app><suffix><env>"
    # prod:  "<app><suffix>"
    # For example, for jira in the dev env, the name would be
    # "jiradev"
    # for jira in the production env, the cname would be 
    # "jira"

    name_parts = [app, suffix, env]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    cname = "".join(name_parts)

    return cname

# each EC2 instance in the ASG will get this host name
def get_host_name( app, env, suffix=""):

    vpc_defs = get_vpc_defs()    

    name_parts = [ app, suffix, env ]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = vpc_defs['delimitter']['value'].join(name_parts)

    return resource_name.title() if vpc_defs['camelcase']['value'] else resource_name

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

    vpc_defs = get_vpc_defs()    

    # if the resource is a db, add a timestamp to the end (including
    # the timestamp makes it easier to restore from snapshots)
    if resource=='rds':
        name_parts = [ app, suffix, env ]
        name_parts = name_parts + [str(int(time.time()))]
    else:
        name_parts = [ app, suffix, env, resource]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = vpc_defs['delimitter']['value'].join(name_parts)

    return resource_name.title() if vpc_defs['camelcase']['value'] else resource_name

# each yac resource has a matching security group, named per this fxn
def get_sg_name(app, env, resource, suffix=""):

    vpc_defs = get_vpc_defs()

    name_parts = [ app, suffix, env, resource, 'sg']

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = vpc_defs['delimitter']['value'].join(name_parts)

    return resource_name.title() if vpc_defs['camelcase']['value'] else resource_name    
   
# get name of the db user to be used with the app input
def get_db_user_name(app):    

    # DB user/role for our stacks are the same as the app name, all
    # lower case
    db_user = app.lower()

    return db_user 
