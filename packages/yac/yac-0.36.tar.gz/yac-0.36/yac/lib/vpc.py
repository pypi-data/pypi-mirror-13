#!/usr/bin/env python
import boto.vpc
import boto.rds

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
                
