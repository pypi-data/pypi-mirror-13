#!/usr/bin/env python
import boto3, json, os, urlparse, subprocess
from yac.lib.template import apply_ftemplate
from yac.lib.paths import get_config_path
from yac.lib.vpc import get_vpc_defs
from yac.lib.version import get_latest_version
from yac.lib.file import FileError
from yac.lib.intrinsic import apply_fxn
from yac.lib.service import is_service_alias, is_service_available_partial_name
from yac.lib.service import get_complete_name, get_alias_from_name, is_service_name_complete
from yac.lib.service import get_service_by_name, get_service_from_file
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_custom_fxn

# determine app alias, service key, and service defintion based on the args
def get_service(app_arg, servicefile_path):

    app_alias = ""
    service_name = ""
    service_descriptor = {}
    servicefile_path = ""

    # if a path to the service descriptor was provided
    if servicefile_path:

        service_descriptor, service_name, servicefile_path = get_service_from_file(servicefile_path)
        app_alias = get_alias_from_name(service_name)

    else:

        # Treat app_arg as the service name. See if it is complete (i.e.
        # includes a version label)
        if is_service_name_complete(app_arg):

            # name is complete
            service_name = app_arg

            app_alias = get_alias_from_name(service_name)

        # Treat app_arg is a service name that lacks a version
        elif is_service_available_partial_name(app_arg):

            # get complete name
            service_name = get_complete_name(app_arg)

            app_alias = get_alias_from_name(service_name)

        # pull the service from the registry
        service_descriptor = get_service_by_name(service_name)

    # get exclusions from service definition

    return service_descriptor, service_name, app_alias, servicefile_path

def get_service_parmeters(app_alias, env_arg, suffix_arg, 
                          service_name, service_descriptor,
                          servicefile_path):

    service_parmeters = {}

    # add params set via cli
    set_variable(service_parmeters,"app",app_alias)
    set_variable(service_parmeters,"env",env_arg)
    set_variable(service_parmeters,"suffix",suffix_arg)
    set_variable(service_parmeters,"service-name",service_name)
    set_variable(service_parmeters,"servicefile-path",servicefile_path)

    # combine static service params with cli params
    service_parmeters.update(service_descriptor["service-params"])

    # get vpc preferences
    vpc_defs = get_vpc_prefs()

    # combine static vpc preferences with service params
    service_parmeters.update(vpc_defs["vpc-prefs"])

    # create dynamic vpc params via an (optional) vpc inputs scripts
    vpc_input_script = get_variable( vpc_defs, "service-inputs","")
    vpc_dynamic_params = apply_custom_fxn(vpc_input_script, service_parmeters)

    # combine dynamic vpc params with service params
    service_parmeters.update(vpc_dynamic_params)

    # create dynamic service params via an (optional) service inputs script
    service_input_script = get_variable(service_descriptor, "service-inputs","")
    service_dynamic_params = apply_custom_fxn(service_input_script, service_parmeters)

    # combine dynamic service input params with service params
    service_parmeters.update(service_dynamic_params)

    # add default values for vpc-related params (proxy, corporate cidr, etc.) if non were provided
    default_vpc_params(service_parmeters)

    return service_parmeters

def default_vpc_params(service_parmeters):

    if not get_variable(service_parmeters,'proxy-port',""):
        set_variable(service_parmeters,'proxy-port',"")

    if not get_variable(service_parmeters,'proxy-cidr',""):
        set_variable(service_parmeters,'proxy-cidr',"")

    if not get_variable(service_parmeters,'corporate-cidr',""):
        set_variable(service_parmeters,'corporate-cidr',"")

    if not get_variable(service_parmeters,'dns-cidr',""):
        set_variable(service_parmeters,'dns-cidr',"0.0.0.0/0")        

    if not get_variable(service_parmeters,'ntp-servers',""):
        set_variable(service_parmeters,'ntp-servers',"0.pool.ntp.org;1.pool.ntp.org;2.pool.ntp.org;3.pool.ntp.org") 

def deploy_app_files(service_descriptor, service_parmeters): 

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

   