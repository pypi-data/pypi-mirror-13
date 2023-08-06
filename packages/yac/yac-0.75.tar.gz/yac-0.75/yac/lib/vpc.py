import os, json, jmespath
import boto.vpc
import boto.rds
from yac.lib.paths import get_config_path
from yac.lib.registry import set_remote_string_w_challenge, get_remote_value, get_registry_keys
from yac.lib.registry import set_local_value, get_local_value, clear_entry_w_challenge

def show_subnets(vpc_friendly_name):

    # get the operative naming standards
    vpc_defs = get_vpc_defs()

    # get the id of the VPC requested
    vpc_id = get_vpc_ids(vpc_friendly_name)[0]

    if vpc_id:

        # Get the subnet ids of the various yac resouces
        public_subnet_ids = get_subnet_ids(vpc_id, vpc_defs['subnets']['public'])
        dmz_subnet_ids = get_subnet_ids(vpc_id, vpc_defs['subnets']['dmz'])
        private_subnet_ids = get_subnet_ids(vpc_id, vpc_defs['subnets']['private'])

        # Get the db subnet group for this vpc
        db_subnet_group = get_db_subnet_groups(vpc_id, vpc_defs['db_subnet_group']['value'])

        print 'id for %s vpc: %s'%(vpc_friendly_name,vpc_id)
        print 'id(s) for public subnets (%s): %s'%(vpc_defs['subnets']['public'], str(public_subnet_ids))
        print 'id(s) for dmz subnets (%s): %s'%(vpc_defs['subnets']['dmz'], str(dmz_subnet_ids))
        print 'id(s) for private subnets (%s): %s'%(vpc_defs['subnets']['private'], str(private_subnet_ids))
        print 'names of db subnet group (%s): %s'%(vpc_defs['db_subnet_group']['value'], str(db_subnet_group))

    else:
        print "could not find vpc"

def get_vpc_names(region='us-west-2'):

    conn = boto.vpc.connect_to_region(region)

    vpcs = conn.get_all_vpcs()
    
    vpc_names = []

    for vpc in vpcs:
    
        if ('Name' in vpc.tags): 
            vpc_names.append(vpc.tags['Name'])

    return vpc_names

def get_vpc_ids( name_search_string="", tag_name='Name', region='us-west-2'):

    conn = boto.vpc.connect_to_region(region)

    vpcs = conn.get_all_vpcs()
    
    vpc_ids = []

    for vpc in vpcs:
    
        if (name_search_string and tag_name in vpc.tags and name_search_string in vpc.tags[tag_name]): 
            # search string matches instance name tag
            vpc_ids.append(str(vpc.id))
        elif not name_search_string:
            # no search string provided so return this address
            vpc_ids.append(str(vpc.id)) 

    return vpc_ids

def get_vpc_cidrs( name_search_string="", tag_name='Name', region='us-west-2' ):

    conn = boto.vpc.connect_to_region(region)

    vpcs = conn.get_all_vpcs()
    
    vpc_cidr = []

    for vpc in vpcs:
    
        if (name_search_string and tag_name in vpc.tags and name_search_string in vpc.tags[tag_name]): 
            # search string matches instance name tag
            vpc_cidr.append(str(vpc.cidr_block))
        elif not name_search_string:
            # no search string provided so return this cidr
            vpc_cidr.append(str(vpc.cidr_block)) 

    return vpc_cidr    

def get_subnet_ids( vpc_id , name_search_string="", tag_name='Name', region='us-west-2'):

    conn = boto.vpc.connect_to_region(region)

    subnets = conn.get_all_subnets()

    subnet_ids = []

    for subnet in subnets:

        # first make sure subnet is in this VPC
        if subnet.vpc_id == vpc_id:

            # if a search string was provided, check for a match
            if (name_search_string and tag_name in subnet.tags and name_search_string in subnet.tags[tag_name]): 
                # search string matches instance name tag
                subnet_ids.append(str(subnet.id))
            elif not name_search_string:
                # no search string provided so return this address
                subnet_ids.append(str(subnet.id)) 

    return subnet_ids  

def get_db_subnet_groups( vpc_id , name_search_string="", region='us-west-2'):

    conn_rds = boto.rds.connect_to_region(region)

    all_subnets_groups = conn_rds.get_all_db_subnet_groups()

    subnets_groups = []

    for subnets_group in all_subnets_groups:

        # first make sure subnet is in this VPC
        if subnets_group.vpc_id == vpc_id:

            # if a search string was provided, check for a match
            if (name_search_string and name_search_string in subnets_group.name): 
                # search string matches instance name tag
                subnets_groups.append(str(subnets_group.name))
            elif not name_search_string:
                # no search string provided so return this address
                subnets_groups.append(str(subnets_group.name))

    return subnets_groups        

def get_vpc_def(jmespath_search):

    vpc_definitions = get_vpc_defs()

    value = jmespath.search(jmespath_search,vpc_definitions)

    if type(value) == 'unicode':
        return str(value)
    else:
        return value

def get_vpc_defs():

    vpc_definitions = get_local_value('vpc_definitions')

    return vpc_definitions

def set_vpc_defs(vpc_def_arg):

    # arg can be a path or a key in the yac registry
    if os.path.exists(vpc_def_arg):
        with open(vpc_def_arg) as vpc_def_arg_fp:
            vpc_defs = json.load(vpc_def_arg_fp)
    else:
        # try retrieving from the registry
        vpc_defs = get_vpc_defs_from_registry(vpc_def_arg)

    if vpc_defs:

        # save task defs to local db
        set_local_value('vpc_definitions',vpc_defs)
    
    return vpc_defs

def clear_vpc_defs():

    set_local_value('vpc_definitions',{})

# register namer into yac registry
def register_vpc_defs(vpc_registry_key, vpc_defs_file):

    with open(vpc_defs_file) as vpc_defs_file_fp:

        vpc_definitions_str = vpc_defs_file_fp.read()

        # set the vpc defs in the registry
        set_remote_string_w_challenge('%s-vpc'%vpc_registry_key, vpc_definitions_str,'temp')

def clear_vpc_defs_from_registry(vpc_registry_key):

    # clear the vpc defs from the registry
    clear_entry_w_challenge('%s-vpc'%vpc_registry_key,'temp')

def get_vpc_defs_from_registry(vpc_def_registry_key):

    vpc_defs = {}

    if vpc_def_registry_key:

        # get vpc defs from registry
        vpc_defs_str = get_remote_value('%s-vpc'%vpc_def_registry_key)

        # convert back to dictionary
        vpc_defs = json.loads(vpc_defs_str)

    return vpc_defs

def get_all_vpc_def_keys():

    vpc_defs = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with -vpc suffix
    for key in registry_keys:

        if '-vpc' in key:
            # remove the naming part
            vpc_defs = vpc_defs + [key.replace('-vpc','')]

    return vpc_defs                    