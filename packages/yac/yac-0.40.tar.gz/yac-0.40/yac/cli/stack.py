import os, sys, json, argparse, getpass, inspect
from sets import Set
import slib # for getting path
from yac.lib.stack import create_stack, stack_exists, get_stack_elements, get_stack_templates
from yac.lib.stack import get_template_variables, combine_stack_templates, get_stack_params
from yac.lib.stack import BUILDING, UPDATING, update_stack, get_num_subnet_layers, cost_stack
from yac.lib.name import get_stack_name, get_cluster_name, get_fqdn, get_db_host_name
from yac.lib.vpc import get_vpc_ids, get_subnet_ids, get_db_subnet_groups
import yac.cli.app

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_exlusions(exlusions_arg, myapp_template_arg=""):

    exclusions = []

    if exlusions_arg:

        # passed via cli

        # use map to strip leading/trailing white spaces
        exclusions = map(str.strip,exlusions_arg.split(',')) if exlusions_arg else []
    
    if myapp_template_arg:

        # check if any exclusions are in template
        stackdef = get_stackdef_from_file(template_path)
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

def are_exclusions_valid(parser, arg):
    
    # use map to strip leading/trailing white spaces
    exclusions = get_exlusions(arg)

    valid_stack_resources = get_stack_elements()

    # compare exclusions input to accepted stack elements. set formed via
    # intersection of accepted elements and exclusions should have same number of 
    # elements as exclusions
    if len(Set(valid_stack_resources) & Set(exclusions)) != len(exclusions):

        parser.error("One of the stack exlusions is invalid. Choose from %s" % (arg,str(valid_stack_resources)))
    
    elif 'asg' in exclusions:
        parser.error("Sorry, at this time an ASG is a mandatory YAC resource and can't be excluded")

    else:
        return arg        

def get_conf_dir():

  # return the abs path to the config directory
  return os.path.join(os.path.dirname(inspect.getfile(slib)),'../config')

def load_user_params(stack_params, params_str):

    if params_str:

        user_params = json.loads(params_str)

        for key in user_params.keys():
            stack_params.append((str(key),user_params[key]))

    return stack_params

def main():

    parser = argparse.ArgumentParser('Print a stack for a YAC application via cloudformation')
    # required args
    parser.add_argument('app',  help='name of the app to build an stack for', 
                                choices=['jira','crowd','confluence','bamboo','hipchat'])
    parser.add_argument('env',  help='the env', 
                                choices=['dev', 'stage', 'prod','archive'])
    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    

    parser.add_argument('--exclude', help='exclude these stack elements. csv list with choices in [i-elb,e-elb,efs,rds,ecs]',
                                          type=lambda x: are_exclusions_valid(parser, x))
    parser.add_argument('--users',   help='the number of users the app will be licensed to support',
                                     choices=["25","50","100","250","500","2000","10000","10000+"],
                                     default= "50")    
    parser.add_argument('-d','--dryrun',  help='dry run the stack change, printing template to stdout', 
                                          action='store_true')
    parser.add_argument('--vpc',     help='the name (or partial name) of the VPC to build stack in (defaults are per naming std)')    
    parser.add_argument('--suffix',  help='app name suffix (allows you to create multiple instances of the same app in the same env)',
                                     default='')      
    parser.add_argument('--myapp',   help='path to the app-specific yac template file for this app (useful to keep your stack configuration in scm)',
                                     type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--desc',    help='the description to put on the stack')
    parser.add_argument('--noecs', help='do not join ec2 instances into an ecs cluster (useful for container dev on dev stacks)',
                                        action='store_true')
    parser.add_argument('--snapshot',help='if creating a new stack with a DB, create DB from this snapshot id',
                                     default='')    

    args = parser.parse_args()

    # get exclusions, which can specified either from cli or in app-specific template file
    exclusions = get_exlusions(args.exclude, args.myapp)

    # get stack name based on app, env, and app suffix
    stack_name = get_stack_name(args.app, args.env, args.suffix)

    # determine if we are building or updating this stack
    action = UPDATING if stack_exists(stack_name) else BUILDING

    # get the templates to use based on the exclusions and myapp arg
    templates_files = get_stack_templates(args.myapp, exclusions)

    # get the template variables for this stack
    template_variables = get_template_variables(args.app, args.env, args.desc)

    # combine the templates into a complete stack template for the stack requested
    stack_template = combine_stack_templates(templates_files, template_variables)

    # get parameters for this stack
    stack_params = get_stack_params(stack_name, action, args.app, args.env, args.vpc, 
                                    args.suffix, args.noecs, args.snapshot, 
                                    exclusions, stack_template)

    # pprint template dictionary to a string
    stack_template_str = json.dumps(stack_template,indent=2)

    # **************************** Print Time! ************************************
 
    if args.dryrun:

        # do a dry-run by printing the stack template and stack parameters to stdout
        stack_params_str = json.dumps(stack_params,indent=2)

        print "stack template %s"%stack_template_str
        print "stack parameters: %s"%stack_params_str

        # calc the cost of this stack, and provide url showing calculation
        response = cost_stack(template_string = stack_template_str, 
                              stack_params    = stack_params)

        print "Dry-run print of stack %s with these resources: %s "%(stack_name,str(get_inclusions(exclusions)))
        print "Cost of this stack can be viewed here: %s"%str(response['Url'])
        print "Make sure to add an EBS volume on services tab with intended size of your home directory."

    else:

        print "%s%s stack named %s for the %s app in the %s env, tuned to support up to %s users%s"%('\033[92m',action,stack_name,args.app,args.env,args.users,'\033[0m')
        print "%sStack includes these resources: %s %s"%('\033[92m',str(get_inclusions(exclusions)),'\033[0m')

        # send 'roger that' text to stdout in green text and give user chance to bail
        raw_input("Hit <enter> to continue..." ) 


        #if action == BUILDING:
        #    response  = create_stack(stack_name = stack_name,
        #                            template_string = stack_template_str, 
        #                            stack_params    = stack_params)
        #else:
        #     response = update_stack(stack_name = stack_name,
        #                            template_string = stack_template_str, 
        #                            stack_params    = stack_params)
    
    if not args.noecs:

        # create the cluster

        # first remove arguments that are n/a for the app cli
        sys.argv = [s for s in sys.argv if 'vpc' not in s] 
        sys.argv = [s for s in sys.argv if 'desc' not in s]
        sys.argv = [s for s in sys.argv if 'noecs' not in s]
        sys.argv = [s for s in sys.argv if 'snapshot' not in s]
        sys.argv = [s for s in sys.argv if 'exclude' not in s]
        
        return yac.cli.app.main()    
