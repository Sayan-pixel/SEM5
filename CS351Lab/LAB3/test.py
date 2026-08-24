import boto3

ec2 = boto3.client("ec2")

print(ec2.describe_regions())