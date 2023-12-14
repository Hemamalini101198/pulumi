import pulumi
import pulumi_aws as aws
import json

queue_type = "standard"

# SQS creation based on the input of queue type
if queue_type == "fifo":
    # Create an AWS SQS FIFO queue
    sqs_queue = aws.sqs.Queue("exampleFifoQueue",
        name="pulumi-queue.fifo",
        fifo_queue=True,
        tags={
            "Environment": "rd",
            "Project": "idz",
            "QueueType": "FIFO"
        }
    )
else:
    # Create an AWS SQS Standard queue
    sqs_queue = aws.sqs.Queue("exampleStandardQueue",
        name="pulumi-queue",
        tags={
            "Environment": "rd",
            "Project": "idz",
            "QueueType": "Standard"
        }
    )

# Define IAM policy
policy = pulumi.Output.all(sqs_queue.arn).apply(lambda queue_arn: {
    "Version": "2012-10-17",
    "Id": "__default_policy_ID",
    "Statement": [
        {
            "Sid": "__owner_statement",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::701829533401:root",
            },
            "Action": "SQS:*",
            "Resource": queue_arn,
        },
    ],
})

# Create SQS Queue Policy
sqs_queue_policy = aws.sqs.QueuePolicy("exampleQueuePolicy",
    queue_url=sqs_queue.id,
    policy=policy,
)

# Export the name and ARN of the queue
pulumi.export('queue_name', sqs_queue.name)
pulumi.export('queue_arn', sqs_queue.arn)
