from pulumi_aws import config, iam
import json
import pulumi
from pulumi_aws import eks

config = pulumi.Config()
desired_size = config.require('desired_size')
min_size = config.require('min_size')
max_nodes = config.require('max_nodes')
instance_types = config.require('instance_types')
capacity_type = config.require('capacity_type')
ami_type = config.require('ami_type')
private_subnet_ids = config.require('private_subnet_ids').split(', ')
public_subnet_ids = config.require('public_subnet_ids').split(', ')
cluster_name = config.require('cluster_name')
node_group_name = config.require('node_group_name')


## EKS Cluster Role
eks_role = iam.Role(
    'eks-iam-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Principal': {
                    'Service': 'eks.amazonaws.com'
                },
                'Effect': 'Allow',
                'Sid': ''
            }
        ],
    }),
)

iam.RolePolicyAttachment(
    'eks-service-policy-attachment',
    role=eks_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSServicePolicy',
)


iam.RolePolicyAttachment(
    'eks-cluster-policy-attachment',
    role=eks_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSClusterPolicy',
)

## Ec2 NodeGroup Role
ec2_role = iam.Role(
    'ec2-nodegroup-iam-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Principal': {
                    'Service': 'ec2.amazonaws.com'
                },
                'Effect': 'Allow',
                'Sid': ''
            }
        ],
    }),
)

iam.RolePolicyAttachment(
    'eks-workernode-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy',
)


iam.RolePolicyAttachment(
    'eks-cni-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy',
)

iam.RolePolicyAttachment(
    'ec2-container-ro-policy-attachment',
    role=ec2_role.id,
    policy_arn='arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly',
)

## EKS Cluster
eks_cluster = eks.Cluster(
    'eks-cluster',
    name=cluster_name,
    role_arn=eks_role.arn,
    tags={
        'Name': 'pulumi-eks-cluster',
    },
    vpc_config=eks.ClusterVpcConfigArgs(
        subnet_ids=private_subnet_ids,
    ),
)

eks_node_group = eks.NodeGroup(
    'eks-node-group',
    cluster_name=eks_cluster.name,
    node_group_name=node_group_name,
    node_role_arn=ec2_role.arn,
    subnet_ids=public_subnet_ids,
    instance_types=[instance_types],
    capacity_type=capacity_type,
    ami_type=ami_type,
    tags={
        'Name': 'pulumi-cluster-nodeGroup',
    },
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=desired_size,
        max_size=max_nodes,
        min_size=min_size,
    ),
)

pulumi.export('cluster-name', eks_cluster.name)

