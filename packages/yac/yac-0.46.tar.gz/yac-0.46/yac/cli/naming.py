#!/usr/bin/env python

import argparse, sys, json, os

from yac.lib.naming import get_namer, register_namer, set_namer, get_host_name
from yac.lib.naming import clear_custom_namer, get_all_naming_standard_keys
from yac.lib.naming import get_namer_code_from_registry

def main():

    parser = argparse.ArgumentParser('Naming standards configurations')

    parser.add_argument('--current',  help='show the current naming standards from the registry (arg is key from the registry)',
                                   action='store_true')
    parser.add_argument('--show',  help='show a naming standards from the registry (arg is key from the registry)')    
    parser.add_argument('--set',   help='set the naming standard to use when building stacks (arg is key from the registry)')
    parser.add_argument('--clear', help='clear the custom naming standard currently in use',
                                   action='store_true')
    parser.add_argument('--list', help='list keys of all naming standards in the registry',
                                   action='store_true') 
    parser.add_argument('--register', help='register a new (or update an existing) naming standards (arg is key for the registry)')
    parser.add_argument('--test',  help='test your namer by getting a resource name')

    # pull out args
    args = parser.parse_args()

    if args.current:

        namer_path = get_namer()

        # pprint naming_std dictionary to a string
        print namer_path

    if args.show:

        namer_code = get_namer_code_from_registry(args.show)

        # pprint naming_std dictionary to a string
        print namer_code        

    elif args.register:

        namer_path = raw_input("Please input filename with path for the python file containing your namer >> ")
        
        if os.path.exists(namer_path):

            register_namer(args.register,namer_path)

            print "Your namer has been registered with yac under the key: %s. Other users can configure yac with your namer via '>> yac naming --set=%s'"%(args.register,args.register)

        else:
            print "File input does not exist. Please try again."

    elif args.set:

        print "Setting yac namer per the '%s' namer in the yac registry."%args.set
        raw_input("Hit Enter to continue >> ")

        set_namer(args.set)

    elif args.clear:

        print "Clearing any customer naming standards currently in use and reverting to default"
        raw_input("Hit Enter to continue >> ")

        clear_custom_namer()

    elif args.list:

        print "Listing naming standards currently available in the registry"
        raw_input("Hit Enter to continue >> ")

        print get_all_naming_standard_keys()                 

    elif args.test:

        print get_host_name(args.test,'dev')
