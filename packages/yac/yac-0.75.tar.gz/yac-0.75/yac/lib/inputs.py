import boto3, jmespath
from sets import Set

def get_vpc_defs_wizard():
    
    #vpc_id = validated_input("enter id of the vpc to build in >> ", 
    #                           "vpc not found, please try again", 
    #                           get_vpcs(),
    #                           input_validation)

    vpc_id = 'vpc-6207ff07'
    private_subnet_ids = validated_array_input("enter the id of a subnet in your private subnet layer >> ", 
                                 "one of more subnets not valid, please try again",
                                  get_subnets(vpc_id,get_azs()),
                                  array_validation)


def validated_input(msg, retry_msg, options, function):
    
    print options

    validation_failed = True
    
    while validation_failed:

        input = raw_input(msg)

        input = input.strip("'")

        # validate the input
        validation_failed = function(input, options,retry_msg)

    return input

def validated_array_input(msg, retry_msg, options, function):
    
    print options

    validation_failed = True
    array_building = True

    print "enter values one at a time, cr when done ..."

    inputs = []

    while validation_failed:

        input = raw_input(msg).strip("'")

        if input:
            inputs.append(input)
        else:
            validation_failed,inputs = function(inputs, options,retry_msg)

def input_validation(input,options,retry_msg):

    # attempt to find the vpc input
    validation_failed = input not in options

    if validation_failed:
        print retry_msg

    return validation_failed

def array_validation(inputs,options,retry_msg):

    # attempt to find the vpc input
    validation_failed = len(Set(inputs) & Set(options)) != len(inputs)

    if validation_failed:
        print retry_msg
        inputs=[]

    return validation_failed, inputs    

# get the ids of the vpcs available to this user
def get_vpcs():

    ec2 = boto3.client('ec2')

    # Environment tag contains VPC_MAPPING values
    vpcs = ec2.describe_vpcs()

    # get id's only
    vpc_ids = jmespath.search("Vpcs[*].VpcId", vpcs)

    return vpc_ids

# get the zones available to this user
def get_azs():

    ec2 = boto3.client('ec2')

    # Environment tag contains VPC_MAPPING values
    azs = ec2.describe_availability_zones()

    # get id's only
    az_names = jmespath.search("AvailabilityZones[*].ZoneName", azs)

    return az_names

# get the subnets available in a given vpc and a given set of 
# availability zones
def get_subnets(vpc_id, availabilty_zones):

    ec2 = boto3.client('ec2')
    
    subnets = ec2.describe_subnets(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        },
        {
            'Name': 'availability-zone',
            'Values': availabilty_zones
        }])

    subnet_ids = jmespath.search('Subnets[*].SubnetId',subnets)

    return subnet_ids

# get_vpc_defs_wizard()