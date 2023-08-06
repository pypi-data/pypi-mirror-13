#!/usr/bin/env python
import os, json, urlparse, boto3
from botocore.exceptions import ClientError
from sets import Set
from yac.lib.file import FileError
from yac.lib.template import apply_ftemplate
from yac.lib.paths import get_config_path
from yac.lib.intrinsic import apply_fxn
from yac.lib.variables import get_variable, set_variable

UPDATING = "Updating"
BUILDING = "Building"

def validate_stock_resources(stock_resources):

    valid_stock_resources = get_all_stock_resources()

    validation_errors = {}

    unsupported_resources = list(Set(stock_resources) - Set(valid_stock_resources))

    if unsupported_resources:
        validation_errors["unsupported-resources"] = unsupported_resources

    return validation_errors

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

def get_all_stock_resources():
    # currently supported stock resources
    # yac developers: feel free to add more!
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

    # get the stock resources specified
    stock_resources = get_variable(service_descriptor,'stock-resources',[])

    # get the stock template files to use based on stock resources specified
    template_files = _get_stock_template_files(stock_resources)

    # Add load-balancer-refs to service_parmeters based on elbs specified.
    # The references are used by the ASG to understand which ELBs are incoming
    load_balancer_refs = []
    if ('i-elb' in stock_resources):
        load_balancer_refs.append({"Ref": "InternalElb"})
    if ('e-elb' in stock_resources):
        load_balancer_refs.append({"Ref": "ExternalElb"})

    set_variable(service_parmeters,"load-balancer-refs",load_balancer_refs) 

    # combine all stock resources into a single stack dictionary
    stack_template = {}
    for key in template_files.keys():
        
        # pull template from file into a dictionary while also rendering any service 
        # parmeters into the dictionary
        this_resource_template = get_stackdef_from_file(template_files[key],
                                                        service_parmeters)

        # merge this resource into the stack definition
        stack_template = update_template(stack_template,this_resource_template) 

    # next add any resources or resource changes specified in the service_descriptor
    if 'CloudFormation' in service_descriptor:
        # merge service-specific resources into the stack definition
        # first render intrinsics
        service_template = apply_fxn(service_descriptor['CloudFormation'], service_parmeters)

        # merge these resources into the stack definition
        stack_template = update_template(stack_template,service_template) 

    return stack_template

def _get_stock_template_files(stock_resources):

    stock_templates = {}

    # stock templates currently supported
    template_map = {
        "asg":   "yac-asg-stack.json",
        "rds":   "yac-db-stack.json",
        "e-elb": "yac-eelb-stack.json",
        "i-elb": "yac-ielb-stack.json",
        "efs":   "yac-efs-stack.json"
    }

    config_path = os.path.join(get_config_path(),'stack')

    for resource_key in stock_resources:

        stock_templates[resource_key] = os.path.join(config_path,template_map[resource_key])

    return stock_templates

# Inputs are two cloud formation templates.
# Merge the to_add_template into the base_template
def update_template(base_template, to_add_template):

    if 'Description' in to_add_template:
        # add a stack-specific description
        base_template['Description'] = to_add_template['Description']

    if 'Conditions' in to_add_template:

        # first make sure Parameters is present in base template
        if 'Conditions' not in base_template:
            base_template['Conditions'] = {}

        for key in to_add_template['Conditions'].keys():

            base_template['Conditions'][key] = to_add_template['Conditions'][key]

    if 'Parameters' in to_add_template:

        # first make sure Parameters is present in base template
        if 'Parameters' not in base_template:
            base_template['Parameters'] = {}

        for key in to_add_template['Parameters'].keys():

            base_template['Parameters'][key] = to_add_template['Parameters'][key]

    if 'Mappings' in to_add_template:

        # first make sure Resources is present in base template
        if 'Mappings' not in base_template:
            base_template['Mappings'] = {}

        for key in to_add_template['Mappings'].keys():

            base_template['Mappings'][key] = to_add_template['Mappings'][key]

    if 'Resources' in to_add_template:

        # first make sure Resources is present in base template
        if 'Resources' not in base_template:
            base_template['Resources'] = {}

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

def deploy_stack_files(service_descriptor, service_parmeters): 

    # get and deploy any files that the service needs before booting
    # (default to empty array in case variable is not defined)
    files_for_boot = get_variable(service_descriptor, 'files-for-boot', [])

    # render service parmeters in the files then deploy 'em
    _load_files(get_variable(service_descriptor, 'files-for-boot'), 
                service_parmeters)

    # get and deply any additional files the service needs before booting from a gold image
    if get_variable(service_parmeters, 'gold-image'):
        
        # (default to empty array in case variable is not defined)
        files_for_gold_image = get_variable(service_descriptor, 'files-for-gold-image',[]) 

        # render service parmeters in the files then deploy 'em
        _load_files(files_for_gold_image, 
                    service_parmeters)

# Render service parmeters into file body, then load files to destination
# Only s3 destinations are currently supported.
def _load_files(files, service_parmeters):

    # assume the file path is relative to the location
    # of the service descriptor file (just like Dockerfile!)
    servicefile_path = get_variable(service_parmeters,"servicefile-path")

    for this_ifile in files:

        # render intrinsics in the file dictionary
        this_file = apply_fxn(this_ifile, service_parmeters)      

        source_path = os.path.join(servicefile_path,this_file['src'])

        if os.path.exists(source_path):

            # replace any service parmeters in the file body and return the 
            # "rendered" file contents as a string
            file_contents_str = apply_ftemplate(source_path, service_parmeters)

            # if destination is s3 bucket
            if is_s3_destination(this_file['dest']):

                # create a 'tmp' directory to hold the rendered file contents
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')

                rendered_file = os.path.join('tmp','rendered_file')

                # write the rendered string into the temp file 
                with open(rendered_file, 'w') as outfile:
                    outfile.write(file_contents_str)

                # copy rendered file to s3 destination 
                cp_to_s3( rendered_file, this_file['dest'])

            # if destination is another local file (mostly used for testing)
            else:

                # make sure destination directory exists
                if not os.path.exists(os.path.dirname(this_file['dest'])):
                    os.makedirs(os.path.dirname(this_file['dest']))

                # write the rendered string into the destination file
                with open(this_file['dest'], 'w') as outfile:
                    outfile.write(file_contents_str)
        else:

            raise FileError( "%s file deploy was not performed. Source file is missing"%source_path )

# returns true if file to be loaded is configured for an s3 destination
def is_s3_destination( destination ):

    s3_destination = False

    # S3 destinations are URL's with s3 as the scheme
    # Use this to detect an S3 destination

    # attempt to parse the destination as a URL
    url_parts = urlparse.urlparse(destination)

    if (url_parts and url_parts.scheme and url_parts.scheme == 's3'):

        s3_destination = True

    return s3_destination

# cp a file to an s3 buckert
# raises an Error if source file does not exists
# raises an subprocess.CalledProcessError if cp fails
def cp_to_s3(source_file, destination_s3_url):

    # make sure source file exists
    if os.path.exists(source_file):            

        # form aws cp command for this file
        aws_cmd = "aws s3 cp %s %s"%( source_file, destination_s3_url)

        try:
            subprocess.check_output( aws_cmd , stderr=subprocess.STDOUT, shell=True )

        except subprocess.CalledProcessError as e:
            raise FileError("Error copying file to s3 destination: %s"%e)

    else:
        raise FileError("Source file %s does not exist"%source_file)        