#!/usr/bin/env python
import os, json
import boto3
from botocore.exceptions import ClientError
from jinja2 import Template
from sets import Set

from yac.lib.config import get_config_path
from yac.lib.naming import get_resource_name, get_sg_name, get_host_name, get_cluster_name
from yac.lib.vpc import get_vpc_defs, get_vpc_ids, get_subnet_ids, get_db_subnet_groups
from yac.lib.app import get_default_container_configs_s3_url, get_app_constants

UPDATING = "Updating"
BUILDING = "Building"

def get_exlusions(exlusions_arg, myapp_template_arg=""):

    exclusions = []

    if exlusions_arg:

        # passed via cli

        # use map to strip leading/trailing white spaces
        exclusions = map(str.strip,exlusions_arg.split(',')) if exlusions_arg else []
    
    if myapp_template_arg:

        # check if any exclusions are in template
        stackdef = get_stackdef_from_file(myapp_template_arg)
        if 'Exclusions' in stackdef:
            exclusions = exclusions + stackdef['Exclusions']

    # include intrinsic exclusions
    
    # if there are only 2 subnet layers, exclude the internal elb
    if get_num_subnet_layers()==2:
        exclusions = exclusions + ['i-elb']

    # remove dupes before returning
    return list(set(exclusions))

def get_inclusions(exclusions):

    valid_stack_resources = get_stack_elements()

    return list(Set(valid_stack_resources) - Set(exclusions))

def pretty_print_resources(resources):

    resource_map = {
        "asg":   "Auto-Scaling Group",
        "efs":   "Elastic File System (for shared home)",
        "i-elb": "Internal ELB (intranet-facing)",
        "e-elb": "External ELB (internet-facing)",
        "rds":   "Relational DB Service"
    }
    pp_resources = "\n"

    for resource_key in resources:
        pp_resources = pp_resources + '* %s: %s\n'%(resource_key,resource_map[resource_key])

    return pp_resources

def get_num_subnet_layers():

    vpc_defs = get_vpc_defs()

    subnet_names = []
    if 'private' in vpc_defs['subnets']:
        subnet_names = subnet_names + [vpc_defs['subnets']['private']]
    if 'dmz' in vpc_defs['subnets']:
        subnet_names = subnet_names + [vpc_defs['subnets']['dmz']]
    if 'public' in vpc_defs['subnets']:
        subnet_names = subnet_names + [vpc_defs['subnets']['public']]


    return len(Set(subnet_names))

def get_stack_elements():
    # possible stack elments for a yac stack, per yac stack diagram
    return ['asg', 'efs', 'rds', 'e-elb', 'i-elb']

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

    try:
        response = client.create_stack(StackName=stack_name,
                                     TemplateBody=template_string,
                                     Parameters = stack_params,
                                     Tags=stack_tags)

        print 'Stack creation in progress - use AWS console to watch construction and/or see errors'

    except ClientError as e:
        
        print 'Stack creation failed: %s'%str(e)
        response = e

    return response


def update_stack( stack_name , 
                  template_string="", 
                  stack_params = None):

    client = boto3.client('cloudformation')

    try:
        response = client.update_stack(StackName=stack_name,
                                     TemplateBody=template_string,
                                     Parameters = stack_params)

        print 'Stack update in progress - use AWS console to watch updates and/or see errors'

    except ClientError as e:
        
        print 'Stack update failed: %s'%str(e)
        response = e

    return response    

def get_stack_tags(sys_argv, inclusions):

    # each stack should include the following
    # 1) the yac command line arg that was used to create it
    # 2) the resources included in the stack

    return [
        {
            "Key": "yac_command",
            "Value": " ".join(['yac'] + sys_argv)
        },
        {
            "Key": "yac_resources",
            "Value": str(inclusions)
        }     
    ]

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
def get_stack_params(stack_name, action, app_arg, env_arg, 
                     suffix_arg, noecs_arg, exclusions, stack_template):

    vpc_defs = get_vpc_defs()

    app_constants = get_app_constants()

    # get the id of the VPC requested. The ASG has no default value but the user
    # can pass on via myapp
    if 'Value' in stack_template['Parameters']['VpcId']:
        vpc_id = stack_template['Parameters']['VpcId']['Value']
    else:
        # use the default vpc for this env
        vpc_search_str = vpc_defs['vpcs'][env_arg]

        vpc_id = get_vpc_ids(vpc_search_str)[0]
    
    # Get the subnet id of the private, public, and dmz subnets in the vpc requested
    private_subnets_ids = get_subnet_ids(vpc_id, vpc_defs['subnets']['private'])
    public_subnets_ids = get_subnet_ids(vpc_id,  vpc_defs['subnets']['public'])
    dmz_subnets_ids = get_subnet_ids(vpc_id,     vpc_defs['subnets']['dmz'])

    # convert subnet arrays into a csv string per CommaDelimitedList param type 
    private_subnets_ids_str = ",".join(private_subnets_ids)
    public_subnets_ids_str = ",".join(private_subnets_ids)
    dmz_subnets_ids_str = ",".join(dmz_subnets_ids)

    # convert availability zones array into a csv string per CommaDelimitedList param type 
    avail_zones_str = ",".join(vpc_defs['availability_zones']['value'])

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
                    {"ParameterKey": "S3Bucket", "ParameterValue": vpc_defs['s3_bucket']['value']},
                    {"ParameterKey": "DnsCidr", "ParameterValue": vpc_defs['dns-cidr']['value']},
                    {"ParameterKey": "NtpServers", "ParameterValue": vpc_defs['ntp_servers']['value']},
                    {"ParameterKey": "CostCenter", "ParameterValue": vpc_defs['cost_center']['value']},
                    {"ParameterKey": "Owner", "ParameterValue": vpc_defs['owner']['value']},
                    {"ParameterKey": "AccessLogsPath", "ParameterValue": get_access_logs_path(app_arg,env_arg,suffix_arg)}]

    # insert "as necessary" ASG stuff

    # The url to the file in s3 that ec2 instances in this stack will use to configure the backups container in restore mode.
    # Typically this file is the same file used to configure the backups container.
    # In restore mode, the container reverses the direction of the file transfers. This "restores" the filesystem of a 
    # freshly minted EC2 instance into the state of its predecessor.
    if ('RestoreConfigs' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['RestoreConfigs']):
        stack_params.append({"ParameterKey": "RestoreConfigs", 
            "ParameterValue": get_default_container_configs_s3_url(app_arg, env_arg, suffix_arg, vpc_defs['s3_bucket']['value'],'backups')})
           
    # the key to use for ssh access to an instance
    if ('KeyName' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['KeyName']):
        stack_params.append({"ParameterKey": "KeyName", "ParameterValue": vpc_defs['ssh-key-default']['value']})

    # the iam role to use for access to aws resources from each ec2 instance
    if ('IamInstanceProfile' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['IamInstanceProfile']):
        stack_params.append({"ParameterKey": "IamInstanceProfile", "ParameterValue": vpc_defs['iam-role-default']['value'] })

    # the ssl cert to use on ELBs
    if ('SSLCert' in stack_template['Parameters'] and 'Value' not in stack_template['Parameters']['SSLCert']):
        stack_params.append({"ParameterKey": "SSLCert", "ParameterValue": vpc_defs['ssl-cert-default']['value'] })
 
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
    if (get_num_subnet_layers()==3 and vpc_defs['corporate-cidr']['value']):
        # join to cluster by specifying cluster name
        stack_params.append({"ParameterKey": "CorporateCidr", "ParameterValue": vpc_defs['corporate-cidr']['value'] })

    # ProxyPort and ProxyCidr are to configure support for outbound proxies (common in 3 layer vpc's)
    if (vpc_defs['outbound-proxy']['name']):
        # join to cluster by specifying cluster name
        stack_params.append({"ParameterKey": "ProxyCidr", "ParameterValue": vpc_defs['outbound-proxy']['cidr'] })
        stack_params.append({"ParameterKey": "ProxyName", "ParameterValue": vpc_defs['outbound-proxy']['name'] })
        stack_params.append({"ParameterKey": "ProxyPort", "ParameterValue": vpc_defs['outbound-proxy']['port'] })
        stack_params.append({"ParameterKey": "HttpsProxy", "ParameterValue": "https://%s:%s"%(vpc_defs['outbound-proxy']['name'],vpc_defs['outbound-proxy']['port']) })

    if 'efs' in exclusions:
        # treat AppEFS as a param
        stack_params.append({"ParameterKey": "AppEFS", "ParameterValue": ""})
    else:
        # remove AppEFS as a param to instead treat it like a Resource
        stack_template['Parameters'].pop('AppEFS')

    # set resource-specific params
    for resource in get_inclusions(exclusions):

        # required params are per the parameters dictionary in the 
        # config/stack/yac-<resource>-stack.json file for 
        # each resource type
        
        if resource=='rds':

            resource_name = get_sg_name(app_arg, env_arg, resource, suffix_arg)
            stack_params.append({"ParameterKey": "DBSGName", "ParameterValue": resource_name})

            # print 'vpc: %s, db grp %s'%(vpc_id,get_db_subnet_groups(vpc_id, vpc_defs['db_subnet_group']['value']))
            db_subnet_group = get_db_subnet_groups(vpc_id, vpc_defs['db_subnet_group']['value'])[0]
            stack_params.append({"ParameterKey": "DBSubnetGroup", "ParameterValue": db_subnet_group})

            if action==BUILDING:

                sys_admin_pwd = 'testing' # get_syadmin_pwd()
                stack_params.append({"ParameterKey": "DBPassword", "ParameterValue": sys_admin_pwd})

                resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
                stack_params.append({"ParameterKey": "DBHostName", "ParameterValue": resource_name})

                # if a gold image exists for this app, build the rds instance from it
                if app_arg in vpc_defs['gold-images']:
                    snapshot_id = vpc_defs['gold-images'][app]['snapshot_id']
                    stack_params.append({"ParameterKey": "CreateDBFromThisSnapshot", "ParameterValue": snapshot_id})

            if action==UPDATING:

                # keep params as is unless rds is being added to an existing stack
                if not get_param_value(stack_name, "CreateDBFromThisSnapshot"):
                    stack_params.append({"ParameterKey": "CreateDBFromThisSnapshot", "ParameterValue": ""})
                else:
                    stack_params.append({"ParameterKey": "CreateDBFromThisSnapshot", "UsePreviousValue": True})

                if not get_param_value(stack_name, "DBPassword"):
                    sys_admin_pwd = 'testing' # get_syadmin_pwd()
                    stack_params.append({"ParameterKey": "DBPassword", "ParameterValue": sys_admin_pwd})
                else:
                    stack_params.append({"ParameterKey": "DBPassword", "UsePreviousValue": True})

                if not get_param_value(stack_name, "DBHostName"):
                    resource_name = get_resource_name(app_arg, env_arg, resource, suffix_arg)
                    stack_params.append({"ParameterKey": "DBHostName", "ParameterValue": resource_name})
                else:
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


def get_syadmin_pwd():
    return getpass.getpass('Enter password for RDS sysadmin user: ')

def get_param_value(stack_name, param_key):

    val=""
    client = boto3.client('cloudformation')

    try:
        response = client.describe_stacks(StackName=stack_name)
        
        for stack in response['Stacks']:
            for parameter in stack['Parameters']:
                if parameter['ParameterKey'] == param_key:
                    val=parameter['ParameterValue']
    except:
        val=""
    
    return val

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

    stack_templates['from-user'] = appstack_from_user if appstack_from_user else ""

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

    # Start with ths asg template (which all templates share)
    # Pull template from file into a dictionary while also rendering any template 
    # variables into the dictionary
    stack_template = get_stackdef_from_file(stack_templates.pop("asg"),template_variables)

    # loop over the remaining stack resources
    for key in stack_templates.keys():
        
        # pull template from file into a dictionary while also rendering any template 
        # variables into the dictionary
        this_stack_template = get_stackdef_from_file(stack_templates[key],
                                                     template_variables)

        if (key == 'from-user'):

            # if user supplied stack-related customizations
            if 'CloudFormation' in this_stack_template:
                # merge user-supplied template into the stack definition
                stack_template = update_template(stack_template,this_stack_template['CloudFormation']) 
            else:
                print stack_templates[key]
        else:
            # merge this resource into the stack definition
            stack_template = update_template(stack_template,this_stack_template) 

        # add ELB references if stack contains an elb
        if (key == 'i-elb' and stack_templates['i-elb']):
            stack_template['Resources']['AppAutoScalingGroup']['Properties']['LoadBalancerNames'].append({"Ref": "InternalElb"})
        if (key == 'e-elb'and stack_templates['e-elb']):
            stack_template['Resources']['AppAutoScalingGroup']['Properties']['LoadBalancerNames'].append({"Ref": "ExternalElb"}) 

    if 'e-elb' not in stack_templates.keys():
        # move the asg to the private subnet since external access isn't needed
        stack_template['Resources']['AppAutoScalingGroup']['Properties']['VPCZoneIdentifier'] = {"Ref" : "PrivateSubnets"}

    return stack_template

# Inputs are two cloud formation templates.
# Merge the to_add_template into the base_template
def update_template(base_template, to_add_template):
    
    if 'Description' in to_add_template:
        # add a stack-specific description
        base_template['Description'] = to_add_template['Description']

    if ('Parameters' in to_add_template and 'Parameters' in base_template):
        for key in to_add_template['Parameters'].keys():

            base_template['Parameters'][key] = to_add_template['Parameters'][key]

    if ('Mappings' in to_add_template and 'Mappings' in base_template):

        for key in to_add_template['Mappings'].keys():

            base_template['Mappings'][key] = to_add_template['Mappings'][key]

    if 'Resources' in to_add_template:

        for key in to_add_template['Resources'].keys():

            base_template['Resources'][key] = to_add_template['Resources'][key]            

    if 'ResourceTweaks' in to_add_template:

        # 'tweak' resources in the standard stack
        # only tweaks implemented so far are to SGs
        for sg_key in to_add_template['ResourceTweaks'].keys():

            if to_add_template['ResourceTweaks'][sg_key]['Type'] == "AWS::EC2::SecurityGroup":

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