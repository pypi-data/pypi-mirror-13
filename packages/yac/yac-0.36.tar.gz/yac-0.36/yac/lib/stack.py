#!/usr/bin/env python
import os, json
import boto3
from jinja2 import Template
from sets import Set

from yac.lib.config import get_config_path
from yac.lib.name import get_naming_std
from yac.lib.vpc import get_vpc_ids

def get_stack_elements():
    # possible stack elments for a yac stack, per yac stack diagram
    return ['asg', 'efs', 'rds', 'e-elb', 'efs', 'i-elb']

def create_stack():

    std_stack_path = os.path.join(get_config_path(),'yac-stack.json')

    file_found = os.path.exists(std_stack_path)

    print "loading stack def from %s. file exists? %s"%(std_stack_path,file_found)

    return "stack print complete"

def get_template_variables(app_arg, env_arg, desc_arg):

    # variables that may need to be rendered into stack templates for 
    # yac apps
    stack_desc = desc_arg if desc_arg else '%s stack for %s environment'%(app_arg.title(), env_arg)

    stackdef_template_vars = {"app": app_arg, 
                             "app_title": app_arg.title(), 
                             "env": env_arg,
                             "desc": stack_desc}

    return stackdef_template_vars

# build stack parameters
def get_stack_params(app_arg, env_arg, vpc_arg, suffix_arg, exclusions):

    naming_std = get_naming_std()

    # get the id of the VPC requested
    vpc_id = get_vpc_ids(vpc_arg)[0]

    # Get the subnet id of the private, public, and dmz subnets in the vpc requested
    private_subnets_ids = get_subnet_ids(vpc_id, naming_std['subnets']['private'])
    public_subnets_ids = get_subnet_ids(vpc_id, naming_std['subnets']['public'])
    dmz_subnets_ids = get_subnet_ids(vpc_id, naming_std['subnets']['dmz'])

    # convert subnet arrays into a csv string per CommaDelimitedList param type 
    private_subnets_ids_str = ",".join(private_subnets_ids)
    public_subnets_ids_str = ",".join(private_subnets_ids)
    dmz_subnets_ids_str = ",".join(dmz_subnets_ids)

    # these are the base set needed for all stacks
    stack_params = [("AppName", app_arg.title()),
                    ("AppEnv", env_arg.title()),
                    ("VpcId", vpc_id),
                    ("PrivateSubnets", private_subnets_ids_str),
                    ("PublicSubnets", public_subnets_ids_str),
                    ("DMZSubnets", dmz_subnets_ids_str)]
    
    # subtract out exclusions
    resource_to_build = Set(get_stack_elements()) - Set(exclusions)

    for resource in resource_to_build:

        # required paras are per the parameters dictionary in the 
        # config/stack/yac-<resource>-stack.json file for 
        # each resource type
        if resource=='asg':
            stack_params.append(("DBHostName", db_host_name))

def get_stack_templates(appstack_arg, exclusions):

    # recedence goes:
    # args
    # envs
    # defaults

    stack_templates = {}

    config_path = os.path.join(get_config_path(),'stack')

    # first get stack templ for auto-scaling group
    # all stack have an asg
    stack_templates['asg'] = os.path.join(config_path,'yac-asg-stack.json')

    #  get app-specific stack templ input by user
    appstack_from_user = appstack_arg if appstack_arg else os.environ.get('YAC_APP_STACK')

    stack_templates['app'] = appstack_from_user if appstack_from_user else ""

    # load db stack templ unless it was excluded
    stack_templates['rds'] = os.path.join(config_path,'yac-db-stack.json') \
                            if 'rds' not in exclusions else ""

    # load e-elb stack templ unless it was excluded
    stack_templates['e-elb'] = os.path.join(config_path,'yac-eelb-stack.json') \
                            if 'e-elb' not in exclusions else ""
    
    # load i-elb stack templ unless it was excluded
    stack_templates['i-elb'] = os.path.join(config_path,'yac-ielb-stack.json') \
                            if 'i-elb' not in exclusions else ""

    # load efs stack templ unless it was excluded
    stack_templates['efs'] = os.path.join(config_path,'yac-efs-stack.json') \
                            if 'efs' not in exclusions else ""

    return stack_templates

def _render_string_variables(string_w_variables, template_vars):

    template = Template(string_w_variables)
    return template.render(template_vars)


def combine_stack_templates(stack_templates, template_variables):

    # start with ths asg template, which all templates share
    stack_template = get_stackdef_from_file(stack_templates.pop("asg"),template_variables)

    # loop over the remaining stack resources
    for key in stack_templates.keys():
        
        # pull template from file into a dictionary while also rendering any provided template 
        # variables into the dictionary
        this_stack_template = get_stackdef_from_file(stack_templates[key],
                                                     template_variables)
        # merge this resource into the stack definition
        stack_template = update_template(stack_template,this_stack_template) 

    return stack_template

# Inputs are two cloud formation templates.
# Merge the to_add_template into the base_template
def update_template(base_template, to_add_template):

    
    if 'Description' in to_add_template:
        # add a stack-specific description
        base_template['Description'] = to_add_template['Description']

    if ('Parameters' in to_add_template and 'Parameters' in base_template):
        # add parameters to suite this stack
        for key in to_add_template['Parameters'].keys():

            base_template['Parameters'][key] = to_add_template['Parameters'][key]

    if ('Mappings' in to_add_template and 'Mappings' in base_template):
        # add mapping unique to this stack
        for key in to_add_template['Mappings'].keys():

            base_template['Mappings'][key] = to_add_template['Mappings'][key]

    if 'Resources' in to_add_template:
        # add resources unique to this stack

        for key in to_add_template['Resources'].keys():

            base_template['Resources'][key] = to_add_template['Resources'][key]            

    if 'ResourceTweaks' in to_add_template:

        # 'tweak' resources in the standard stack
        for sg_key in to_add_template['ResourceTweaks'].keys():

            if to_add_template['ResourceTweaks'][sg_key]['Type'] == "AWS::EC2::SecurityGroup":

                # this is a security group

                for second_tier_key in to_add_template['ResourceTweaks'][sg_key]['Properties'].keys():

                    if second_tier_key == "SecurityGroupEgress":

                        # add special egress rule
                        base_template = _append_sg_rule(base_template, 
                                                        to_add_template,
                                                        sg_key,
                                                        "SecurityGroupEgress")
                
                    elif second_tier_key == "SecurityGroupIngress":

                        # add special ingress rule
                        base_template = _append_sg_rule(base_template, 
                                                        to_add_template,
                                                        sg_key,
                                                        "SecurityGroupIngress")

    return base_template

# returns stack template as a dictionary
def get_stackdef_from_file(template_path, template_vars={}):

    stack_definitions = {}

    if (template_path and os.path.exists(template_path)):
        
        # get the host-related config parameters
        with open(template_path) as stack_defs:

            stack_definitions_str = stack_defs.read()

            # if template variables provided, render variables in the
            # stack definitions
            if template_vars:
                stack_definitions_str = _render_string_variables(stack_definitions_str,template_vars)

            # convert task def string to dictionary
            stack_definitions = json.loads(stack_definitions_str)

    return stack_definitions

def stack_exists(stack_name):

    client = boto3.client('cloudformation')

    try:
        response = client.describe_stacks(StackName=stack_name)
        return len(response['Stacks'])>0
    except:
        return False