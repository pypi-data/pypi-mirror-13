#!/usr/bin/env python
import boto3, jmespath, json, os, urlparse, subprocess
from jinja2 import Template
from yac.lib.config import get_config_path
from yac.lib.name import get_cname
from yac.lib.name import get_naming_std

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

        subprocess.check_output( aws_cmd , stderr=subprocess.STDOUT, shell=True )

    else:
        raise Exception("Source file does not exist")

# get constants associated with yac apps
def get_catalina_options(catalina_file):

    catalina_file_path = os.path.join( get_config_path(),'app',catalina_file)

    catalina_options = ""
    if (catalina_file_path and os.path.exists(catalina_file_path)):

        # use the default naming standard
        with open(catalina_file_path) as catalina_file_path_fp:
            catalina_options = catalina_file_path_fp.read()
            # convert carriage returns to spaces
            catalina_options = catalina_options.replace('\n',' ')

    return catalina_options

# get constants associated with yac apps
def get_app_constants():

    app_const_file = os.path.join( get_config_path(),'app','yac-app-const.json')

    app_constants = {}
    if (app_const_file and os.path.exists(app_const_file)):

        # use the default naming standard
        with open(app_const_file) as app_const_fp:
            app_constants = json.load(app_const_fp)
                            
    return app_constants

def get_user_count(app_template_arg, user_arg):

    # precedence for user count is:
    # 1) as defined in user-supplied app template file
    # 2) as defined in cli args

    app_template = get_taskdefs_from_file(app_template_arg)

    if 'Users' in app_template:
        user_count = app_template['Users']
    else:
        user_count = user_arg

    return user_count
    
def get_template_variables(app, env, suffix, user_count):

    app_contants = get_app_constants()
    naming_std = get_naming_std()

    # prefix the env with suffix (when there are multiple instances in this env)
    suffix_then_env = '%s/%s'%(suffix,env) if suffix else env

    template_vars = {
        "app": app, 
        "app_title": app.title(), 
        "suffix_then_env": suffix_then_env,
        "cname": get_cname(app,env),
        "app_log": app_contants['logs'][app]['file'],
        "s3_bucket": naming_std['s3_bucket']['value'],
        "app_port": app_contants['ports'][app],
        "debug_port": app_contants['ports'][app]+1,
        "organization": naming_std['container-org']['value'],
        "app_container_memory": app_contants['sizing'][user_count]['app_container_memory'],
        "heap_size": app_contants['sizing'][user_count]['app_heap_size'],
        "backups_configs_path": get_default_container_configs_s3_url(app, env, suffix, 
                                                                     naming_std['s3_bucket']['value'], 'backups'),
        "logs_configs_path": get_default_container_configs_s3_url(app, env, suffix, 
                                                                  naming_std['s3_bucket']['value'],'logs'),
    }

    # add proxy variables if an outbound proxy is configured
    if naming_std['outbound-proxy']['name']:

        name_port = '%s:%s'%(naming_std['outbound-proxy']['name'],naming_std['outbound-proxy']['port'])
        template_vars["http_proxy"] =  'http://%s'%(name_port)
        template_vars["https_proxy"] = 'https://%s'%(name_port)
        template_vars["no_proxy"] = naming_std['outbound-proxy']['no-proxy']

        catalina_proxy_options = get_catalina_options("catalina-proxy-opts")
        catalina_proxy_options = _render_string_variables(catalina_proxy_options,
                                                          {"proxy_host": naming_std['outbound-proxy']['name'],
                                                           "proxy_port": naming_std['outbound-proxy']['port'],
                                                           "jvm_no_proxy": naming_std['outbound-proxy']['jvm-no-proxy'] })
    else:
        catalina_proxy_options = ""

    # add jvm-related variables
    catalina_options = get_catalina_options("catalina-opts")
    catalina_options = _render_string_variables(catalina_options,template_vars)

    template_vars["catalina_options"] = catalina_options + " " + catalina_proxy_options

    # The yac_backup_config_defaults template variable
    # is defined in the app constants and contains variables (paths, s3 bucket, etc.)
    # So, we must render the variables before adding yac_backup_config_defaults to
    # the variable dictionary
    app_default_backups = _render_string_variables(json.dumps(app_contants['backups'][app],indent=2),
                                                   template_vars)

    template_vars["yac_backup_config_defaults"] = app_default_backups

    return template_vars

def get_app_templates(app_template_arg):

    app_templates = {}

    config_path = os.path.join(get_config_path(),'app')

    # first get app templ common to all yac apps
    app_templates['yac'] = os.path.join(config_path,'yac-taskdef.json')

    # get app-specific app templ input by user
    app_templates['user'] = app_template_arg

    return app_templates

def combine_app_templates(templates_files, template_variables):

    # start with ths base template, which all templates share
    app_template = get_taskdefs_from_file(templates_files['yac'],template_variables)

    if templates_files['user']:

        # pull template from file into a dictionary while also rendering any template 
        # variables into the dictionary
        user_app_template = get_taskdefs_from_file(templates_files['user'],template_variables)

        # merge into main template
        app_template = update_template(app_template,user_app_template['ECS']) 

    return app_template

# combine standard yac and app-specific task definitions
def update_template(standard_taskdef,app_taskdef):          

    if 'containerTweaks' in app_taskdef:

        # for each tweaked container
        for tweak in app_taskdef['containerTweaks']:

            # find the container in containerDefintions that this tweak applies to
            for containerIdx, containerDef in enumerate(standard_taskdef['containerDefinitions']):

                if containerDef['name'] == tweak['name']:

                    # for each tweak to this container
                    for tweak_key in tweak.keys():

                        if tweak_key == 'environment_additions':
                             # append this environment variable
                            standard_taskdef['containerDefinitions'][containerIdx]['environment'] = \
                                standard_taskdef['containerDefinitions'][containerIdx]['environment'] + \
                                tweak[tweak_key]                           
                        else:
                            # overwrite the corresponding key in the standard task def
                            standard_taskdef['containerDefinitions'][containerIdx][tweak_key] = tweak[tweak_key]

    if 'containerExclusions' in app_taskdef:

        containers_to_keep = []

        # for each container to exlude
        for exclusion_name in app_taskdef['containerExclusions']:

            # find the container in containerDefintions that this exclusion applies to
            for containerIdx, containerDef in enumerate(standard_taskdef['containerDefinitions']):

                if containerDef['name'] != exclusion_name:
                    # any containers not mentioned as exclusions are keepers
                    containers_to_keep.append(standard_taskdef['containerDefinitions'][containerIdx])

        standard_taskdef['containerDefinitions'] = containers_to_keep

    if 'volumes' in app_taskdef:

        # replace volumes with volumes in app task def
        standard_taskdef['volumes'] = app_taskdef['volumes']

    if 'containerDefinitions' in app_taskdef:

        for container in app_taskdef['containerDefinitions']:
            # add this container
            standard_taskdef['containerDefinitions'].append(container)        

    return standard_taskdef    

def get_taskdefs_from_file(task_definition_file, template_vars={}):
        
    task_definitions = {}

    if (task_definition_file and os.path.exists(task_definition_file)):
        
        # get the host-related config parameters
        with open(task_definition_file) as task_defs:

            task_definitions_str = task_defs.read()

            # if template variables provided, render variables in the
            # task definitions
            if template_vars:
                task_definitions_str = _render_string_variables(task_definitions_str,template_vars)

            # convert task def string to dictionary
            task_definitions = json.loads(task_definitions_str)

    return task_definitions


def upload_app_files(app_taskdef,template_vars): 

    if 'containerDefinitions' in app_taskdef:

        for container in app_taskdef['containerDefinitions']:

            if 'files' in container:

                # the files portion of the container definition is a yak-hack to the ECS taskdefinition
                # json format. Pop it out of the dictionary while loading the file
                _load_files(container.pop('files'), template_vars)

# Load files specified in start configs
# Only s3 destinations are currently supported.
def _load_files(files, template_vars):

    for file_key in files:

        this_file = files[file_key]        

        # if destination is s3 bucket
        if is_s3_destination(this_file['dest']):

            # replace any template variables in the file before storing to S3
            with open(this_file['src'], 'r') as source_file:
                template = Template(source_file.read())

            # create a 'tmp' directory to hold the rendered source file
            if not os.path.exists('tmp'):
                os.makedirs('tmp')

            rendered_file = os.path.join('tmp','rendered_file')

            # print 'rendered file: %s'%rendered_file
            with open(rendered_file, 'w') as outfile:
                outfile.write(template.render(template_vars))                

            # replace any template variables in the destination
            destination =  _render_string_variables(this_file['dest'],template_vars)

            # copy file to s3 bucket
            cp_to_s3( rendered_file, destination)

        else:

            print '%s file upload was not performed. Only s3 destinations are currently supported.'%this_file['src']

def _render_string_variables(string_w_variables, template_vars):

    template = Template(string_w_variables)
    return template.render(template_vars)

# create a new task definition, or create a new revision of an existing 
# task definition
# returns taskdef revision number, as generated by ECS
def _create_task_definition(client, 
                            task_definition_name, 
                            task_definitions):

    revision = 0

    family = task_definition_name
        
    # register task definition
    response = client.register_task_definition(family=family,
                  containerDefinitions=task_definitions['containerDefinitions'],
                  volumes=task_definitions['volumes'])

    # get the new revision number from ECS response
    revision = response['taskDefinition']['revision']

    return revision

def _new_cluster_needed(client, cluster_name):

    # first see if this cluster exists
    response = client.describe_clusters(clusters=[cluster_name])

    cluster_exists = response['clusters'] and len(response['clusters'])>0

    # a new cluster is need if the cluster doesn't already exist
    return not cluster_exists

# print a new stack
def create_or_update_cluster( cluster_name , 
                    task_definitions,
                    desired_count=1):

    client = boto3.client('ecs')

    # A new task definition is need for all updates to cluster software
    # Create the task definition.
    # Task definition name should match cluster name
    revision = _create_task_definition(client, 
                                       cluster_name, 
                                       task_definitions)

    # determine if a new cluster is needed
    new_cluster_needed = _new_cluster_needed(client, cluster_name)

    if new_cluster_needed:

        print 'Creating %s cluster with %s:%s service with count=%s ...'%(cluster_name,
                          cluster_name,revision ,desired_count)
        # Cluster does not yet exist and this is not a dry run, so
        # create the cluster
        response = client.create_cluster(clusterName=cluster_name)

        # Associate the new task definition with the cluster.
        # Service name, cluster name, and task def name should all match
        response = client.create_service(
                        cluster=cluster_name,
                        serviceName=cluster_name,
                        taskDefinition='%s:%s'%(cluster_name,revision),
                        desiredCount=desired_count)

    elif not new_cluster_needed:

        # Cluster already exists and this is not a dry run

        print 'Updating %s cluster with %s:%s service with count=%s ...'%(cluster_name,
                          cluster_name,revision ,desired_count)

        # Update the cluster with the latest rev of the task definition.
        # Service name, cluster name, and task def name should all match
        response = client.update_service(
                        cluster=cluster_name,
                        service=cluster_name,
                        taskDefinition='%s:%s'%(cluster_name,revision),
                        desiredCount=desired_count)

# stop a cluster
def stop_cluster( cluster_name ):

    client = boto3.client('ecs')

    # get the services on this cluster
    services = client.describe_services(cluster=cluster_name,services=[cluster_name])

    if (len(services['services'])==1 and services['services'][0]['taskDefinition']):

        # get the task definition for this service in this cluster
        task_definition=str(services['services'][0]['taskDefinition'])

        print 'Stopping %s cluster with %s service ...'%(cluster_name,
                          cluster_name )

        # stop the cluster by setting desiredCount to 0
        response = client.update_service(
                        cluster=cluster_name,
                        service=cluster_name,
                        taskDefinition=task_definition,
                        desiredCount=0) 

# start a cluster
def start_cluster( cluster_name ):

    client = boto3.client('ecs')

    # get the services on this cluster
    services = client.describe_services(cluster=cluster_name,services=[cluster_name])

    if (len(services['services'])==1 and services['services'][0]['taskDefinition']):

        # get the task definition for this service in this cluster
        task_definition=str(services['services'][0]['taskDefinition'])

        print 'Stopping %s cluster with %s service ...'%(cluster_name,
                          cluster_name )

        # start the cluster by setting desiredCount to 1
        response = client.update_service(
                        cluster=cluster_name,
                        service=cluster_name,
                        taskDefinition=task_definition,
                        desiredCount=1)


# returns the url to the location in s3 where an containers configuration
# file should be stored
def get_default_container_configs_s3_url(app, env, suffix, s3_bucket, container):   

    file_name = '%s-%s.json'%(app,container)
    name_parts = [s3_bucket, app, suffix, env, file_name]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    file_path = '/'.join(name_parts)

    url = 's3://%s'%(file_path)

    return url