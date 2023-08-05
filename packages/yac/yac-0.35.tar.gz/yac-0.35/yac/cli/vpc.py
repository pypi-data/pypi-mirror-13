import argparse, json, os
from yac.lib.vpc import get_vpc_ids, get_subnet_ids, get_db_subnet_groups
from yac.lib.name import get_naming_std
from yac.lib.config import get_config_path

def show_vpc_primer():

    with open(os.path.join( get_config_path(),'yac-vpc-primer')) as usage_file:
        yac_vpc_primer = usage_file.read()

    print yac_vpc_primer

def show_mapping_primer():

    with open(os.path.join( get_config_path(),'yac-mapping-primer')) as usage_file:
        mapping_primer = usage_file.read()

    print mapping_primer 

def show_subnets(vpc_friendly_name, naming_std_file):

    # get the operative naming standards
    naming_std = get_naming_std(naming_std_file)

    if (naming_std and 
        'valid' in naming_std and 
        naming_std['valid']==True):

        # get the id of the VPC requested
        vpc_id = get_vpc_ids(vpc_friendly_name)[0]

        # Get the subnet ids of the various yac resouces
        eelb_subnet_ids = get_subnet_ids(vpc_id, naming_std['subnets']['e-elb'])
        ielb_subnet_ids = get_subnet_ids(vpc_id, naming_std['subnets']['i-elb'])
        asg_subnet_ids = get_subnet_ids(vpc_id, naming_std['subnets']['asg'])
        rds_subnet_ids = get_subnet_ids(vpc_id, naming_std['subnets']['rds'])
        efs_subnet_ids = get_subnet_ids(vpc_id, naming_std['subnets']['efs'])

        print 'id for %s vpc: %s'%(vpc_friendly_name,vpc_id)
        print 'id(s) for %s e-elb subnets: %s'%(naming_std['subnets']['e-elb'], str(eelb_subnet_ids))
        print 'id(s) for %s i-elb subnets: %s'%(naming_std['subnets']['i-elb'], str(ielb_subnet_ids))
        print 'id(s) for %s asg subnets: %s'%(naming_std['subnets']['asg'], str(asg_subnet_ids))
        print 'id(s) for %s rds subnets: %s'%(naming_std['subnets']['rds'], str(rds_subnet_ids))
        print 'id(s) for %s efs subnets: %s'%(naming_std['subnets']['efs'], str(efs_subnet_ids))
        print 'vpc resources chosen are based on this naming standard:'
        print json.dumps(naming_std, 
                        sort_keys=True,
                        indent=4, 
                        separators=(',', ': '))
    else:

        print 'The naming standard provided is not valid'

def main():

    parser = argparse.ArgumentParser('YAC VPC primer and subnet lookups')
    # required args
    parser.add_argument('-p','--vpcprimer', 
                        help='give me a primer on vpcs and vpc sub-netting',
                        action='store_true')
    parser.add_argument('-m','--mappingprimer', 
                        help='give me an overview on configuring yac to map resources to my vpc subnets')    
    parser.add_argument('-v','--vpc', 
                        help='test yac subnet lookups - find vpcs with this name string')
    parser.add_argument('-n', '--namestd',
                        help='name of naming standard file to use (defaults to subnets named [public,dmz,private])')
    args = parser.parse_args()

    if args.vpcprimer:
        show_vpc_primer()

    elif args.mappingprimer:
        show_mapping_primer()        

    elif args.vpc:
        show_subnets(args.vpc, args.namestd)

    elif args.namestd and not args.vpc:
        print 'If you provide a naming standard file, you must also provide a VPC to perform lookup into.'

