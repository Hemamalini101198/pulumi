import pulumi
import pulumi_aws as aws

config = pulumi.Config()
db_name = config.require('db_name')
engine_type = config.require('engine_type')
instance_class = config.require('instance_class')
username = config.require('username')
password = config.require('password')
allocated_storage = config.require('allocated_storage')
vpc_id = config.require('vpc_id')
max_allocated_storage = config.require('max_allocated_storage')
final_snapshot_identifier = config.require('final_snapshot_identifier')
subnet_ids = config.require('subnet_ids')

# Create a new security group
rds_security_group = aws.ec2.SecurityGroup("rds-security-group",
    description="Security group for RDS instance",
    vpc_id=vpc_id,
    egress=[{
        "description": "Allow all outbound traffic",
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": ["0.0.0.0/0"],
    }],
    ingress=[{
        "description": "Allow MySQL",
        "from_port": 5432,
        "to_port": 5432,
        "protocol": "tcp",
        "cidr_blocks": ["0.0.0.0/0"],
    }],
)


# Create an RDS Subnet Group
rds_subnet_group = aws.rds.SubnetGroup("rds-subnet-group",
    subnet_ids=["subnet_ids"],  
)

# Create RDS instance with the new security group and subnet group
rds_instance = aws.rds.Instance("rds-instance",
    identifier=db_name,
    engine=engine_type,
    instance_class=instance_class,
    username=username,
    password=password,
    allocated_storage=allocated_storage,
    max_allocated_storage=max_allocated_storage,
    storage_type="gp2",
    publicly_accessible=True,
    multi_az=False,
    storage_encrypted=True,
    vpc_security_group_ids=[rds_security_group.id],
    performance_insights_enabled=True,
    performance_insights_retention_period=7,
    final_snapshot_identifier=final_snapshot_identifier,
    skip_final_snapshot=False,
    copy_tags_to_snapshot=True,
    deletion_protection=True,
    db_subnet_group_name=rds_subnet_group.name,
)

# Export RDS instance properties
pulumi.export("rds_instance_id", rds_instance.id)
pulumi.export("rds_instance_endpoint", rds_instance.endpoint)
