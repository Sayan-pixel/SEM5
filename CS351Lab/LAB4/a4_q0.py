import boto3

# Create an EC2 client.
ec2_client = boto3.client("ec2")

# Retrieve information about the current AWS region.
response = ec2_client.describe_regions()

# Display the available AWS regions.
for region in response["Regions"]:
    print(region["RegionName"])