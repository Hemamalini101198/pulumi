import pulumi
import pulumi_aws as aws
import json

# Creation of S3 bucket with a private ACL and a website configuration.
s3_bucket = aws.s3.Bucket(
    "s3_bucket",
    bucket="test-bucket-pulumi-1",
    acl="private",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
        error_document="index.html"
    ),
    tags={"Name": "test-bucket"},
)

# Bucket Public Access Block to enforce private access to the bucket.
public_access_block = aws.s3.BucketPublicAccessBlock(
    "public_access_block",
    bucket=s3_bucket.id,
    block_public_acls=False,
    block_public_policy=False,
    ignore_public_acls=False,
    restrict_public_buckets=False,
)

# Bucket Ownership Controls for specifying how object ownership is attributed.
s3_bucket_ownership_controls = aws.s3.BucketOwnershipControls(
    "s3_bucket_ownership_controls",
    bucket=s3_bucket.id,
    rule=aws.s3.BucketOwnershipControlsRuleArgs(
        object_ownership="BucketOwnerPreferred",
    ),
)

# Export the website endpoint URL
pulumi.export("bucket_endpoint", s3_bucket.website_endpoint)
