import pulumi
import pulumi_aws as aws

# Get CloudFront Origin Request Policy
cloudfront_origin_request_policy = aws.cloudfront.get_origin_request_policy(
    name="Managed-CORS-S3Origin",
)

# Get CloudFront Cache Policy
cloudfront_cache_policy = aws.cloudfront.get_cache_policy(
    name="Managed-CachingOptimized",
)

# Get CloudFront Response Headers Policy
cloudfront_response_headers_policy = aws.cloudfront.get_response_headers_policy(
    name="Managed-SimpleCORS",
)

# Define an S3 static website origin
s3_origin = aws.cloudfront.DistributionOriginArgs(
    domain_name="test-bucket-pulumi-1.s3-website.ap-south-1.amazonaws.com",
    origin_id="test-bucket-pulumi-1.s3-website.ap-south-1.amazonaws.com",
    custom_origin_config={
        "http_port": 80,
        "https_port": 443,
        "origin_protocol_policy": "http-only",  # or "https-only" or "match-viewer"
        "origin_ssl_protocols": ["TLSv1", "TLSv1.1", "TLSv1.2"],
    },
)

# Create CloudFront Distribution
cf_s3_distribution = aws.cloudfront.Distribution(
    "cf_s3_distribution",
    enabled=True,
    is_ipv6_enabled=True,
    default_cache_behavior={
        "allowedMethods": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
        "cachedMethods": ["GET", "HEAD"],
        "targetOriginId": s3_origin.origin_id,
        "viewerProtocolPolicy": "redirect-to-https",
        "minTtl": 0,
        "defaultTtl": 3600,
        "maxTtl": 86400,
        "cachePolicyId": cloudfront_cache_policy.id,
        "originRequestPolicyId": cloudfront_origin_request_policy.id,
        "responseHeadersPolicyId": cloudfront_response_headers_policy.id,
    },
    origins=[s3_origin],
    price_class="PriceClass_All",
    restrictions={"geoRestriction": {"restrictionType": "none"}},
    tags={
        "Description": "pulumi-test",
    },
    viewer_certificate={"cloudfrontDefaultCertificate": True},
)

# Export CloudFront Distribution properties
pulumi.export('cf_distribution_id', cf_s3_distribution.id)
pulumi.export('cf_domain_name', cf_s3_distribution.domain_name)

# Set up a Pulumi stack
stack = pulumi.get_stack()
pulumi.export('stack_name', stack)

