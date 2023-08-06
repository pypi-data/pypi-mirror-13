#!/usr/bin/env python
import os, json
import boto3
from botocore.exceptions import ClientError
from sets import Set
from yac.lib.paths import get_config_path
from yac.lib.intrinsic import apply_fxn
from yac.lib.variables import get_variable, set_variable

UPDATING = "Updating"
BUILDING = "Building"

def get_inclusions(exclusions):

    valid_stack_resources = get_stack_elements()

    return list(Set(valid_stack_resources) - Set(exclusions))

def pretty_print_resources(resources):

    resource_map = {
        "asg":   "  Auto-Scaling Group",
        "efs":   "  Elastic File System (for shared home)",
        "i-elb": "Internal ELB (intranet-facing)",
        "e-elb": "External ELB (internet-facing)",
        "rds":   "  Relational DB Service"
    }
    pp_resources = "\n"

    for resource_key in resources:
        pp_resources = pp_resources + '* %s: %s\n'%(resource_key,resource_map[resource_key])

    return pp_resources

def get_stack_elements():
    # possible stack elments for a yac stack, per yac stack diagram
    return ['asg', 'efs', 'rds', 'e-elb', 'i-elb']

# determine cost of a new stack
def cost_stack( template_string="", stack_params = None ):

    cost_response = ""

    client = boto3.client('cloudformation')

    try:

        response = client.estimate_template_cost(TemplateBody=template_string,
                                                 Parameters = stack_params)

        cost_response = str(response['Url'])

    except ClientError as e:
        
        cost_response = 'Stack costing failed: %s'%str(e)

    return cost_response

def create_stack( stack_name , 
                  template_string="", 
                  stack_params = [],
                  stack_tags = []):

    client = boto3.client('cloudformation')

    response = client.create_stack(StackName=stack_name,
                                 TemplateBody=template_string,
                                 Parameters = stack_params,
                                 Tags=stack_tags)

    print 'Stack creation in progress - use AWS console to watch construction and/or see errors'

    return response


def update_stack( stack_name , 
                  template_string="", 
                  stack_params = []):

    client = boto3.client('cloudformation')

    response = client.update_stack(StackName=stack_name,
                                 TemplateBody=template_string,
                                 Parameters = stack_params)

    print 'Stack update in progress - use AWS console to watch updates and/or see errors'

    return response       

def get_stack_templates(service_descriptor, service_parmeters):

    exclusions = get_variable(service_parmeters,'exclusions',[])

    # get the stack template files to use based on the exclusions
    template_files = _get_stack_template_files(exclusions)

    # Add load-balancer-refs to service_parmeters based on elb exclusions.
    # The references are used by the ASG to understand which ELBs are incoming
    load_balancer_refs = []
    if ('i-elb' not in exclusions):
        load_balancer_refs.append({"Ref": "InternalElb"})
    if ('e-elb' not in exclusions):
        load_balancer_refs.append({"Ref": "ExternalElb"})

    set_variable(service_parmeters,"load-balancer-refs",load_balancer_refs) 

    # Start with ths asg template (which all templates share)
    # Pull template from file into a dictionary while also rendering any service 
    # parmeters into the dictionary
    stack_template = get_stackdef_from_file(template_files.pop("asg"),
                                            service_parmeters)

    # loop over the remaining stack resources
    for key in template_files.keys():
        
        # pull template from file into a dictionary while also rendering any service 
        # parmeters into the dictionary
        this_stack_template = get_stackdef_from_file(template_files[key],
                                                     service_parmeters)

        # merge this resource into the stack definition
        stack_template = update_template(stack_template,this_stack_template) 

    # next add any resources or resource changes specified in the service_descriptor
    if 'CloudFormation' in service_descriptor:
        # merge user-supplied template into the stack definition

        # first render intrinsics
        user_template = apply_fxn(service_descriptor['CloudFormation'], service_parmeters)

        # merge this(these) resources into the stack definition
        stack_template = update_template(stack_template,user_template) 

    return stack_template

def _get_stack_template_files(exclusions):

    stack_templates = {}

    config_path = os.path.join(get_config_path(),'stack')

    # first get stack templ for auto-scaling group
    # all stack have an asg
    stack_templates['asg'] = os.path.join(config_path,'yac-asg-stack.json')

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
        for sg_key in to_add_template['ResourceTweaks'].keys():

            # assume Security group changes are additions
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

            # add property changes
            else:

                for second_tier_key in to_add_template['ResourceTweaks'][sg_key]['Properties'].keys():

                    base_template['Resources'][sg_key]['Properties'][second_tier_key] = to_add_template['ResourceTweaks'][sg_key]['Properties'][second_tier_key]                     

    return base_template

def _append_sg_rule(base_template, to_add_template, sg_key, rule_type):

    for egress_rule in to_add_template['ResourceTweaks'][sg_key]['Properties'][rule_type]:

        # add and rules to base template
        base_template['Resources'][sg_key]['Properties'][rule_type].append(egress_rule)

    return base_template    

# returns stack template as a dictionary.
# render any yac intrinsics present in the dictionary
def get_stackdef_from_file(template_path, service_parmeters={}):

    stack_definitions = {}

    if (template_path and os.path.exists(template_path)):
        
        with open(template_path) as stack_defs:

            stack_definitions = json.load(stack_defs)

        # render yac intrinsics in the stack definition
        stack_definitions = apply_fxn(stack_definitions, service_parmeters) 

    return stack_definitions

def stack_exists(stack_name):

    client = boto3.client('cloudformation')

    try:
        response = client.describe_stacks(StackName=stack_name)
        return len(response['Stacks'])>0
    except:
        return False