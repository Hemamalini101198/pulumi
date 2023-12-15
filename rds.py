import pulumi
import pulumi_aws as aws

config = pulumi.Config()
db_name = config.require('db_name')
engine_type = config.require('engine_type')
instance_class = config.require('instance_class')
username = config.require('username')
password = config.require('password')
allocated_storage = config.require('allocated_storage')
max_allocated_storage = config.require('max_allocated_storage')
vpc_security_group_ids = config.require('vpc_security_group_ids')
final_snapshot_identifier = config.require('final_snapshot_identifier')

# Create RDS instance
rds_db = aws.rds.Instance("rds_db",
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
    vpc_security_group_ids=["vpc_security_group_ids"],
    performance_insights_enabled=True,
    performance_insights_retention_period=7,
    final_snapshot_identifier=final_snapshot_identifier,
    skip_final_snapshot=False,
    copy_tags_to_snapshot=True,
    deletion_protection=True,
)

# Export RDS instance properties
pulumi.export("rds_db_id", rds_db.id)
pulumi.export("rds_db_endpoint", rds_db.endpoint)
