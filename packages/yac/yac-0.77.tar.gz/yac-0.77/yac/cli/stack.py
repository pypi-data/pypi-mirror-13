import os, sys, json, argparse, getpass, inspect, pprint
from colorama import Fore, Style
from botocore.exceptions import ClientError
from yac.lib.file import FileError
from yac.lib.stack import create_stack, update_stack, cost_stack
from yac.lib.stack import BUILDING, UPDATING, stack_exists, get_stack_templates
from yac.lib.stack import pretty_print_resources, deploy_stack_files
from yac.lib.service import get_service, get_service_parmeters
from yac.lib.naming import set_namer, get_stack_name
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_fxn, INSTRINSIC_ERROR_KEY
from yac.lib.vpc import get_vpc_prefs

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('Print a yac service via cloudformation')
    # required args
    parser.add_argument('service',  help='service name or service alias for the service to print'), 
     
    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    
    parser.add_argument('-e',
                        '--env',  help='the environment to build stack cluster for', 
                                  choices=  ['dev','stage','prod'],
                                  default= "dev")
    parser.add_argument('--suffix',  help='to create multiple instances of the same app in the same env (e.g. confluence-intranet, confluence-tech)',
                                     default='') 
    parser.add_argument('-d',
                        '--dryrun',  help='dry run the stack change, printing template to stdout', 
                                     action='store_true')   
    parser.add_argument('-s',
                        '--status', help='show stack status, including names of all stack elements',
                                    action='store_true')                                       
     
    parser.add_argument('--sf',   help='path to the service descriptor file for this service',
                                   type=lambda x: is_valid_file(parser, x))

    args = parser.parse_args()

    # determine service defintion, complete service name, and service alias based on the args
    service_descriptor, service_name, service_alias, servicefile_path = get_service(args.service, args.sf) 

    # set the resource namer to use for this service
    set_namer(service_descriptor)

    # get vpc preferences in place
    vpc_prefs = get_vpc_prefs()

    # get the service parameters for use with yac-ref's in service templates
    service_parmeters = get_service_parmeters(service_alias, args.env, args.suffix, 
                                              service_name, service_descriptor,
                                              servicefile_path, vpc_prefs)

    print service_parmeters
    
    # get stack name
    stack_name = get_stack_name(service_parmeters)  

    # determine if we are building or updating this stack
    action = UPDATING if stack_exists(stack_name) else BUILDING

    # get cloud formation template for the service requested and apply yac intrinsic 
    # functions (yac-ref, etc.) using  the service_parmeters
    stack_template = get_stack_templates(service_descriptor, 
                                         service_parmeters)

    # Get any reference errors recorded in the service parameters. Each represents
    # a value that should have been rendered into either the stack template, but wasn't.
    reference_errors = get_variable(service_parmeters,INSTRINSIC_ERROR_KEY,"")

    # get the stock resources spec'd by the service
    stock_resources = get_variable(service_parmeters,'stock-resources',[])

    # pprint stack template to a string
    stack_template_str = json.dumps(stack_template,indent=2)

    # **************************** Print Time! ************************************
 
    if args.dryrun:

        print(Fore.GREEN)

        print "%s (dry-run) the %s service aliased as '%s' in the %s env"%(action,service_name,service_alias,args.env)
        
        print "Service includes these 'stock' resources: %s"%(pretty_print_resources(stock_resources))
        
        if reference_errors:
            pp = pprint.PrettyPrinter(indent=4)
            print "Service templates include reference errors. Each should be fixed before doing an actual print."
            print pp.pprint(reference_errors)

        print_template = raw_input("Print stack template to stdout? (y/n)> ")

        if print_template and print_template=='y':
            print "Stack template:\n%s"%stack_template_str
            print "Sanity check the template above."


        estimate_cost = raw_input("Estimate the cost of the resources required by this service? (y/n)> ")

        if estimate_cost and estimate_cost=='y':

            # calc the cost of this stack, and provide url showing calculation
            cost_response = cost_stack(template_string = stack_template_str, 
                                       stack_params    = [])
            print "Cost of the resources for this service can be viewed here: %s"%(cost_response)

        print(Style.RESET_ALL)                      

    else:

        # for reals ...
        print(Fore.GREEN)

        if not reference_errors:
            
            print "%s the %s service aliased as '%s' in the %s env"%(action,service_name,service_alias,args.env)
            print "Stack includes these 'stock' resources: %s"%(pretty_print_resources(stock_resources))

            # give user chance to bail
            raw_input("Hit <enter> to continue..." )

            print(Style.RESET_ALL) 

            # create the service stack
            try:

                # deploy any configurations files required by the service
                deploy_app_files(service_descriptor, service_parmeters)

                if action == BUILDING:
                    response  = create_stack(stack_name = stack_name,
                                            template_string = stack_template_str)
                else:
                     response = update_stack(stack_name = stack_name,
                                            template_string = stack_template_str)
            
            except ClientError as e:
                print 'Service creation failed: %s'%str(e)

            except FileError as e:
                print 'Service creation failed: %s'%str(e.msg)                

        else:
            pp = pprint.PrettyPrinter(indent=4)
            print "Service templates include reference errors. Each must be fixed before a stack print can be performed."
            print pp.pprint(reference_errors)

        print(Style.RESET_ALL)            
