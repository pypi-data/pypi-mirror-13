import argparse, json, os
from yac.lib.vpc import get_vpc_defs, register_vpc_defs, get_vpc_ids, get_subnet_ids
from yac.lib.vpc import get_db_subnet_groups, set_vpc_defs, get_vpc_defs_from_registry
from yac.lib.vpc import show_subnets, get_all_vpc_def_keys, clear_vpc_defs, clear_vpc_defs_from_registry
from yac.lib.paths import get_config_path

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('Set and view my vpc constants (for vpc modeling, and stack-related variables)')

    # required args
    parser.add_argument('--test', 
                        help='test subnet lookups - find subnets in vpcs with this name string')
    parser.add_argument('--current',  help='show the current vpc definition from the registry (arg is key from the registry)',
                                   action='store_true')
    parser.add_argument('--show',  help='show a vpc definition from the registry (arg is key from the registry)')    
    parser.add_argument('--set',   help='set the vpc definition to use when building stacks (arg is key from the registry or a path to a file containing the defs)')
    parser.add_argument('--list',  help='list keys of all vpc definitions in the registry',
                                   action='store_true') 
    parser.add_argument('--register', help='register a new (or update an existing) vpc definition (arg is key for the registry)')
    parser.add_argument('--clear', help='clear a vpc definition from registry (arg of "local" will clear def currently in use locally')    
    
    args = parser.parse_args()       

    if args.test:

        show_subnets(args.test)

    if args.current:

        vpc_defs = get_vpc_defs()

        print json.dumps(vpc_defs, indent=4)

    if args.show:

        vpc_defs = get_vpc_defs_from_registry(args.show)

        print json.dumps(vpc_defs,indent=4)        

    if args.register:

        vpc_def_path = raw_input("Please input filename with path for the json file containing your vpd defintions >> ")
        
        if os.path.exists(vpc_def_path):

            register_vpc_defs(args.register,vpc_def_path)

            print "Your vpc defintions have been registered with yac under the key: '%s'. Other users can configure yac with these vpc defs via '>> yac vpc --set=%s'"%(args.register,args.register)

        else:
            print "File input does not exist. Please try again."

    if args.set:

        print "Setting yac vpc defintions per '%s'."%args.set
        raw_input("Hit Enter to continue >> ")

        set_vpc_defs(args.set)

    if args.list:

        print "The following vpc definitions are currently available in the registry"
        print get_all_vpc_def_keys() 

    if args.clear:

        if args.clear == 'local':
            print "Clearing vpc definitions currently in use"
            raw_input("Hit Enter to continue >> ")
            clear_vpc_defs()
        else:
            # make sure key is legit
            vpc_defs = get_vpc_defs_from_registry(args.clear)
            if vpc_defs:
                print "Clearing the '%s' vpc definitions from registry"%args.clear
                raw_input("Hit Enter to continue >> ")
                clear_vpc_defs_from_registry(args.clear)
            else:
                print "VPC definitions with the '%s' key do not exist in the registry"%args.clear                

