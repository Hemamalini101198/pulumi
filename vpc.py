import pulumi
import pulumi_aws as aws

config = pulumi.Config()
project_name = config.require('project_name')
# env = config.require('env')
vpc_cidr = config.require('vpc_cidr_range')
public_subnet_cidr = config.require('public_subnet_cidr')
private_subnet_cidr = config.require('private_subnet_cidr')
public_sub_availability_zone = config.require('public_sub_availability_zone')
private_sub_availability_zone = config.require('private_sub_availability_zone')

# VPC creation
vpc = aws.ec2.Vpc(
    "vpc",
    cidr_block=vpc_cidr,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": project_name + "-vpc"},
)
 
# Internet Gateway creation
igw = aws.ec2.InternetGateway(
    "igw",
    vpc_id=vpc.id,
    tags={"Name": project_name + "-igw"},
)
 
# Routing Table creation for public subnets
public_route_table = aws.ec2.RouteTable(
    "public",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
    tags={"Name": project_name + "-publicsubnet-rt"},
)
 
# Public Subnet creation
public_subnet = aws.ec2.Subnet(
    "public_subnet",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidr,
    availability_zone=public_sub_availability_zone,
    map_public_ip_on_launch=True,
    tags={"Name": project_name + "-publicsubnet"},
)
 
# Private Subnet creation
private_subnet = aws.ec2.Subnet(
    "private_subnet",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidr,
    availability_zone=private_sub_availability_zone,
    tags={"Name": project_name + "-privatesubnet"},
)
 
# Routing Table Association for public subnet
public_association = aws.ec2.RouteTableAssociation(
    "public_association", subnet_id=public_subnet.id, route_table_id=public_route_table.id
)
 
# Elastic IP for NAT Gateway
nat_ip = aws.ec2.Eip(
    "nat_ip", 
    tags={"Name": project_name + "-eip"}
)
 
# NAT Gateway creation
nat_gateway = aws.ec2.NatGateway(
    "nat_gateway",
    allocation_id=nat_ip.id,
    subnet_id=public_subnet.id,
    tags={"Name": project_name + "-natgw"},
)
 
# Routing Table for private subnet
private_route_table = aws.ec2.RouteTable(
    "private",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": nat_gateway.id}],
    tags={"Name": project_name + "-privatesubnet-rt"},
)
 
# Routing Table Association for private subnet
private_association = aws.ec2.RouteTableAssociation(
    "private_association", subnet_id=private_subnet.id, route_table_id=private_route_table.id
)
 
# Export VPC ID for reference in other stacks or resources
pulumi.export("vpc_id", vpc.id)
