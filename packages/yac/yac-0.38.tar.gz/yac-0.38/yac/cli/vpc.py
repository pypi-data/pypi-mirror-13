import argparse, json, os
from yac.lib.vpc import get_vpc_ids, get_subnet_ids, get_db_subnet_groups
from yac.lib.name import get_naming_std
from yac.lib.config import get_config_path

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

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
    parser.add_argument('-v','--vpc', 
                        help='test yac subnet lookups - find subnets in vpcs with this name string')
    parser.add_argument('-n', '--namestd',
                        help='path to naming standard file to use',
                        type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()       

    if args.vpc:
        show_subnets(args.vpc, args.namestd)

    elif args.namestd and not args.vpc:
        print 'If you provide a naming standard file, you must also provide a VPC to perform lookup into.'

    print 'id for %s vpc: %s'%('TBD', 'TBD')
    print 'id(s) for public subnets: %s'%'TBD'
    print 'id(s) for dmz subnets: %s'%'TBD'
    print 'id(s) for private subnets: %s'%'TBD'
