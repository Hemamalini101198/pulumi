import pulumi
import pulumi_tls as tls
import pulumi_aws as aws

config = pulumi.Config()
key_name = config.require('key_name')
instance_type = config.require('instance_type')
instance_ami = config.require('instance_ami')
instance_name = config.require('instance_name')
vpc_id = config.require('vpc_id')
vpc_security_group_ids = config.require('security_group')
subnet_id =  config.require('subnet_id')
volume_size = config.require('volume_size')
security_group_name = config.require('security_group_name')

ssh_key = tls.PrivateKey(
    "generated",
    algorithm="RSA",
    rsa_bits=4096,
)

aws_key = aws.ec2.KeyPair(
    "generated",
    key_name=key_name,
    public_key=ssh_key.public_key_openssh,
    opts=pulumi.ResourceOptions(parent=ssh_key),
)

# Store the private key in the bucket
private_key_object = aws.s3.BucketObject("privateKeyObject",
    bucket="pulumi-pem-keys",
    key="private.pem",
    content=ssh_key.private_key_pem,
    server_side_encryption="aws:kms",
)

# Create a instance
if vpc_security_group_ids:
    server = aws.ec2.Instance(
        instance_name,
        key_name=aws_key.key_name,
        instance_type=instance_type,
        ami=instance_ami,
        subnet_id=subnet_id,
        associate_public_ip_address=True,
        root_block_device={
        "volume_size": volume_size,
        "volume_type": "gp2"
        },
        tags={
            "Name": instance_name,
        },
        vpc_security_group_ids=[vpc_security_group_ids],
    )

else:
    security_group = aws.ec2.SecurityGroup(
        security_group_name,
        vpc_id=vpc_id,
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=["0.0.0.0/0"],
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    server = aws.ec2.Instance(
        instance_name,
        key_name=aws_key.key_name,
        instance_type=instance_type,
        ami=instance_ami,
        subnet_id=subnet_id,
        associate_public_ip_address=True,
        root_block_device={
        "volume_size": volume_size,
        "volume_type": "gp2"
        },
        tags={
            "Name": instance_name,
        },
        vpc_security_group_ids=security_group.id,
    )


pulumi.export('private_key_pem', ssh_key.private_key_pem)
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)


