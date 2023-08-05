import argparse, json, os
from yac.lib.vpc import get_vpc_defs, register_vpc_defs, get_vpc_ids, get_subnet_ids
from yac.lib.vpc import get_db_subnet_groups, set_vpc_defs, get_vpc_defs_from_registry
from yac.lib.vpc import show_subnets, get_all_vpc_def_keys, clear_vpc_defs
from yac.lib.config import get_config_path

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('YAC VPC primer and subnet lookups')

    # required args
    parser.add_argument('--vpc', 
                        help='test yac subnet lookups - find subnets in vpcs with this name string')
    parser.add_argument('--current',  help='show the current vpc definition from the registry (arg is key from the registry)',
                                   action='store_true')
    parser.add_argument('--show',  help='show a vpc definition from the registry (arg is key from the registry)')    
    parser.add_argument('--set',   help='set the vpc definition to use when building stacks (arg is key from the registry)')
    parser.add_argument('--list',  help='list keys of all vpc definitions in the registry',
                                   action='store_true') 
    parser.add_argument('--register', help='register a new (or update an existing) vpc definition (arg is key for the registry)')
    parser.add_argument('--clear', help='clear the vpc definitionsin use',
                                   action='store_true')    
    
    args = parser.parse_args()       

    if args.vpc:

        show_subnets(args.vpc)

    if args.current:

        vpc_defs = get_vpc_defs()

        vpc_defs_d = { str(key):value for key,value in vpc_defs.items() }

        print json.dumps(vpc_defs_d,indent=4)

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

        print "Setting yac vpc defintions per the '%s' definitions in the yac registry."%args.set
        raw_input("Hit Enter to continue >> ")

        set_vpc_defs(args.set)

    if args.list:

        print "Listing vpc definitions currently available in the registry"
        raw_input("Hit Enter to continue >> ")

        print get_all_vpc_def_keys() 

    if args.clear:

        print "Clearing vpc definitions currently in use"
        raw_input("Hit Enter to continue >> ")

        clear_vpc_defs()            

