#!/usr/bin/env python
import os, json
import boto
import boto3
import boto.cloudformation
import boto.ec2
import boto.ec2.elb
import boto.rds
from jinja2 import Template
from sets import Set
import boto3

from yac.lib.config import get_config_path
from yac.lib.name import get_naming_std, get_resource_name, get_sg_name, get_host_name, get_cluster_name
from yac.lib.vpc import get_vpc_ids, get_subnet_ids, get_db_subnet_groups
from yac.lib.app import get_backup_config_s3_url, get_app_constants

UPDATING = "Updating"
BUILDING = "Building"

def get_num_subnet_layers():

    naming_std = get_naming_std()

    subnet_names = [naming_std['subnets']['private'],naming_std['subnets']['dmz'],naming_std['subnets']['public']]

    return len(Set(subnet_names))

def get_stack_elements():
    # possible stack elments for a yac stack, per yac stack diagram
    return ['asg', 'efs', 'rds', 'e-elb', 'efs', 'i-elb']

# determine cost of a new stack
def cost_stack( template_string="", stack_params = None ):

    client = boto3.client('cloudformation')

    response = client.estimate_template_cost(TemplateBody=template_string,
                                             Parameters = stack_params)

    return response

def create_stack( stack_name , 
                  template_string="", 
                  stack_params = None,
                  stack_tags = []):

    client = boto3.client('cloudformation')

    response = client.create_stack(StackName=stack_name,
                                 TemplateBody=template_string,
                                 Parameters = stack_params,
                                 Tags=stack_tags)
    return response

def update_stack( stack_name , 
                  template_string="", 
                  stack_params = None):

    client = boto3.client('cloudformation')

    response = client.update_stack(StackName=stack_name,
                                 TemplateBody=template_string,
                                 Parameters = stack_params)
    return response    

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
def get_stack_params(action, app_arg, env_arg, vpc_arg, suffix_arg, noecs_arg, exclusions, stack_template):

    naming_std = get_naming_std()

    app_constants = get_app_constants()

    # get the id of the VPC requested
    if vpc_arg:
        # use the vpc requested via cli
        vpc_search_str = vpc_arg        
    else:
        # use the default vpc for this env
        vpc_search_str = naming_std['vpcs'][env_arg]

    vpc_id = get_vpc_ids(vpc_search_str)[0]
    
    # Get the subnet id of the private, public, and dmz subnets in the vpc requested
    private_subnets_ids = get_subnet_ids(vpc_id, naming_std['subnets']['private'])
    public_subnets_ids = get_subnet_ids(vpc_id,  naming_std['subnets']['public'])
    dmz_subnets_ids = get_subnet_ids(vpc_id,     naming_std['subnets']['dmz'])

    # convert subnet arrays into a csv string per CommaDelimitedList param type 
    private_subnets_ids_str = ",".join(private_subnets_ids)
    public_subnets_ids_str = ",".join(private_subnets_ids)
    dmz_subnets_ids_str = ",".join(dmz_subnets_ids)

    # convert availability zones array into a csv string per CommaDelimitedList param type 
    avail_zones_str = ",".join(naming_std['availability_zones']['value'])

    # these are the base set needed for all stacks (per the ASG stack template)
    stack_params = [{"ParameterKey": "AppName", "ParameterValue": app_arg.title()},
                    {"ParameterKey": "AppEnv", "ParameterValue": env_arg.title()},
                    {"ParameterKey": "ASGName", "ParameterValue": get_resource_name(app_arg, env_arg, 'asg', suffix_arg)},
                    {"ParameterKey": "AppSGName", "ParameterValue": get_sg_name(app_arg, env_arg, 'asg', suffix_arg)},
                    {"ParameterKey": "HostName", "ParameterValue": get_host_name( app_arg, env_arg, suffix_arg )},
                    {"ParameterKey": "VpcId", "ParameterValue": vpc_id},
                    {"ParameterKey": "PrivateSubnets", "ParameterValue": private_subnets_ids_str},
                    {"ParameterKey": "PublicSubnets", "ParameterValue": public_subnets_ids_str},
                    {"ParameterKey": "DMZSubnets", "ParameterValue": dmz_subnets_ids_str},
                    {"ParameterKey": "AvailabilityZones", "ParameterValue": avail_zones_str},
                    {"ParameterKey": "S3Bucket", "ParameterValue": naming_std['s3_bucket']['value']},
                    {"ParameterKey": "DnsCidr", "ParameterValue": naming_std['dns-cidr']['value']},
                    {"ParameterKey": "AccessLogsPath", "ParameterValue": get_access_logs_path(app_arg,env_arg,suffix_arg)}]

    # insert "as necessary" ASG stuff

    # the s3 url to the file instance restore configuration file
    if ('RestoreConfigs' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['RestoreConfigs']):
        stack_params.append({"ParameterKey": "RestoreConfigs", "ParameterValue": get_backup_config_s3_url(app_arg, env_arg,naming_std['s3_bucket']['value'])})
           
    # the key to use for ssh access to an instance
    if ('KeyName' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['KeyName']):
        stack_params.append({"ParameterKey": "KeyName", "ParameterValue": naming_std['ssh-key-default']['value']})

    # the iam role to use for access to aws resources from each ec2 instance
    if ('IamInstanceProfile' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['IamInstanceProfile']):
        stack_params.append({"ParameterKey": "IamInstanceProfile", "ParameterValue": naming_std['iam-role-default']['value'] })

    # the ssl cert to use on ELBs
    if ('SSLCert' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['SSLCert']):
        stack_params.append({"ParameterKey": "SSLCert", "ParameterValue": naming_std['ssl-cert-default']['value'] })
 
     # the health check to use on ELBs
    if ('HealthCheckPath' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['HealthCheckPath']):
        stack_params.append({"ParameterKey": "HealthCheckPath", "ParameterValue": app_constants['healthcheck'][app_arg] })
   
    # this is a tad confusing, but the idea is allow the stack builder to choose to not join the ec2 instances
    # in the stack to an ecs cluster. useful in dev envs.
    if not noecs_arg:
        # join to cluster by specifying cluster name
        stack_params.append({"ParameterKey": "ClusterName", "ParameterValue": get_cluster_name(app_arg, env_arg, suffix_arg) })

    # CorporateCidr is for 3 layer subnets where private layer is connected via direct connect to the
    # coporate network
    if (get_num_subnet_layers()==3 and naming_std['corporate-cidr']['value']):
        # join to cluster by specifying cluster name
        stack_params.append({"ParameterKey": "CorporateCidr", "ParameterValue": naming_std['corporate-cidr']['value'] })

    # ProxyPort and ProxyCidr are to configure support for outbound proxies (common in 3 layer vpc's)
    if (naming_std['outbound-proxy']['name']):
        # join to cluster by specifying cluster name
        stack_params.append({"ParameterKey": "ProxyCidr", "ParameterValue": naming_std['outbound-proxy']['cidr'] })
        stack_params.append({"ParameterKey": "ProxyPort", "ParameterValue": naming_std['outbound-proxy']['port'] })

    # subtract out exclusionsProxyCidr
    resource_to_build = Set(get_stack_elements()) - Set(exclusions)

    if 'efs' in exclusions:
        # treat AppEFS as a param
        stack_params.append({"ParameterKey": "AppEFS", "ParameterValue": ""})

    for resource in resource_to_build:

        # required paras are per the parameters dictionary in the 
        # config/stack/yac-<resource>-stack.json file for 
        # each resource type
        
        if resource=='rds':

            resource_name = get_sg_name(app_arg, env_arg, resource, suffix_arg)
            stack_params.append({"ParameterKey": "DBSGName", "ParameterValue": resource_name})

            db_subnet_group = get_db_subnet_groups(vpc_id, naming_std['db_subnet_group']['value'])[0]
            stack_params.append({"ParameterKey": "DBSubnetGroup", "ParameterValue": db_subnet_group})

            if action==BUILDING:

                sys_admin_pwd = 'testing' # getpass.getpass('Enter password for RDS sysadmin user: ')
                stack_params.append({"ParameterKey": "DBPassword", "ParameterValue": sys_admin_pwd})

                resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
                stack_params.append({"ParameterKey": "DBHostName", "ParameterValue": resource_name})

            if action==UPDATING:
                # keep params as is
                stack_params.append({"ParameterKey": "DBPassword", "UsePreviousValue": True})
                stack_params.append({"ParameterKey": "DBHostName", "UsePreviousValue": True})                 

        if resource=='i-elb':

            resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
            stack_params.append({"ParameterKey": "InternalElbName", "ParameterValue": resource_name})

        if resource=='e-elb':

            resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
            stack_params.append({"ParameterKey": "ExternalElbName", "ParameterValue": resource_name})

        if resource=='efs':

            resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
            stack_params.append({"ParameterKey": "EFSName", "ParameterValue": resource_name})

    return stack_params

def get_access_logs_path(app_arg, env_arg, suffix_arg):

    name_parts = [ app_arg, suffix_arg, env_arg, 'access_logs']

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    access_logs_path = '/'.join(name_parts)

    return access_logs_path

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

        # add ELB references as appropriate
        if (key == 'i-elb' and stack_templates['i-elb']):
            stack_template['Resources']['AppAutoScalingGroup']['Properties']['LoadBalancerNames'].append({"Ref": "InternalElb"})
        if (key == 'e-elb'and stack_templates['e-elb']):
            stack_template['Resources']['AppAutoScalingGroup']['Properties']['LoadBalancerNames'].append({"Ref": "ExternalElb"}) 

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