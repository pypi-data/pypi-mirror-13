import os, sys, json, argparse, getpass, inspect
from colorama import Fore, Back, Style
from yac.lib.stack import create_stack, stack_exists, get_stack_elements, get_stack_templates
from yac.lib.stack import get_template_variables, combine_stack_templates, get_stack_params
from yac.lib.stack import BUILDING, UPDATING, update_stack, get_num_subnet_layers, cost_stack, get_stack_tags
from yac.lib.stack import get_exlusions, get_inclusions, pretty_print_resources
from yac.lib.naming import get_stack_name, get_cluster_name
from yac.lib.app import get_user_count
from yac.lib.vpc import get_vpc_defs
import yac.cli.app


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

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

def main():

    parser = argparse.ArgumentParser('Print a stack for a YAC application via cloudformation and ECS')
    # required args
    parser.add_argument('app',  help='name of the app to build an stack for', 
                                choices=['jira','crowd','confluence','bamboo','hipchat'])  
    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    
    parser.add_argument('-e',
                        '--env',  help='the environment to build stack cluster for', 
                                  choices=  ['dev','stage','prod'],
                                  default= "prod")
    parser.add_argument('-d',
                        '--dryrun',  help='dry run the stack change, printing template to stdout', 
                                     action='store_true')   
    parser.add_argument('-s',
                        '--status',help='show status status, including names of all stack elements',
                                     default='')                                       
    parser.add_argument('--exclude', help='exclude these stack elements. csv list with choices in [i-elb,e-elb,efs,rds,ecs]',
                                          type=lambda x: are_exclusions_valid(parser, x))
    parser.add_argument('--users',   help='the number of users the app will be licensed to support',
                                     choices=["25","50","100","250","500","2000","10000","10000+"],
                                     default= "50")
    parser.add_argument('--suffix',  help='to create multiple instances of the same app in the same env (e.g. confluence-intranet, confluence-tech)',
                                     default='')      
    parser.add_argument('--myapp',   help='path to the app-specific yac template file for this app (useful to keep your stack configuration in scm)',
                                     type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--desc',    help='the description to put on the stack')
    parser.add_argument('--noecs', help='do not join ec2 instances into an ecs cluster (useful for container dev on dev stacks)',
                                        action='store_true')   

    args = parser.parse_args()

    # make sure vpc definitions are in place. without these we can't do much
    if not get_vpc_defs():
        print "VPC definitions not yet in place. See >> yac vpc -h"
        exit()

    # get exclusions, which can specified either from cli or in app-specific template file
    exclusions = get_exlusions(args.exclude, args.myapp)

    # get the user count
    user_count = get_user_count(args.myapp, args.users) 

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
    stack_params = get_stack_params(stack_name, action, args.app, args.env, 
                                    args.suffix, args.noecs, exclusions, stack_template)
    
    # get the resources included in this stack
    inclusions = get_inclusions(exclusions)
    
    # get tags for this stack
    stack_tags = get_stack_tags(sys.argv, inclusions)

    # pprint template dictionary to a string
    stack_template_str = json.dumps(stack_template,indent=2)

    # **************************** Print Time! ************************************
 
    if args.dryrun:

        # do a dry-run by printing the stack template and stack parameters to stdout
        stack_params_str = json.dumps(stack_params,indent=2)

        # calc the cost of this stack, and provide url showing calculation
        response = cost_stack(template_string = stack_template_str, 
                              stack_params    = stack_params)

        print(Fore.GREEN)
        print "%s (dry-run) stack named %s for the %s app in the %s env, tuned to support up to %s users"%(action,stack_name,args.app,args.env,user_count)
        print "Stack includes these resources: %s"%(pretty_print_resources(inclusions))
        print "Cost of this stack can be viewed here: %s"%(str(response['Url']))
        print "(cost note: make sure to add an EBS volume on services tab with intended size of your home directory.)"
        print(Style.RESET_ALL)

        print_template = raw_input("Print stack template to stdout? (y/n)> ")
        

        if print_template and print_template=='y':
            print(Fore.GREEN) 
            print "stack template %s"%stack_template_str
            print "stack parameters: %s"%stack_params_str
            print(Style.RESET_ALL)

    else:

        print(Fore.GREEN)
        print "%s stack named %s for the %s app in the %s env, tuned to support up to %s users"%(action,stack_name,args.app,args.env,user_count)
        print "Stack includes these resources: %s"%(pretty_print_resources(inclusions))
        print(Style.RESET_ALL)

        # give user chance to bail
        raw_input("Hit <enter> to continue..." ) 
        

        if action == BUILDING:
            response  = create_stack(stack_name = stack_name,
                                    template_string = stack_template_str, 
                                    stack_params    = stack_params,
                                    stack_tags = stack_tags)
        else:
             response = update_stack(stack_name = stack_name,
                                    template_string = stack_template_str, 
                                    stack_params    = stack_params)
    
    if not args.noecs:

        # create the cluster

        # first remove arguments that are n/a for the app cli
        sys.argv = [s for s in sys.argv if 'status' not in s] 
        sys.argv = [s for s in sys.argv if 'desc' not in s]
        sys.argv = [s for s in sys.argv if 'noecs' not in s]
        sys.argv = [s for s in sys.argv if 'exclude' not in s]
        
        return yac.cli.app.main()    
