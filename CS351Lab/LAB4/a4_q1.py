# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 1

import boto3

def setup_and_launch():
    # Initialize boto3 clients
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    ec2_resource = boto3.resource('ec2', region_name='ap-south-1')
    
    key_name = 'assignment4-key'
    sg_name = 'assignment4-sg'
    
    # 1. Create a new Key Pair
    try:
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
        with open(f"{key_name}.pem", "w") as file:
            file.write(key_pair['KeyMaterial'])
        print(f"Created new Key Pair: {key_name} (saved to {key_name}.pem)")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidKeyPair.Duplicate' in str(e):
            print(f"Key Pair {key_name} already exists.")
        else:
            raise e

    # 2. Create a new Security Group with Port 80 and 22 open
    try:
        response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description='Security group for Assignment 4 HTTP server'
        )
        sg_id = response['GroupId']
        print(f"Created new Security Group: {sg_id}")
        
        # Add rules for HTTP (80) and SSH (22)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            print(f"Security Group {sg_name} already exists. Getting its ID...")
            response = ec2_client.describe_security_groups(GroupNames=[sg_name])
            sg_id = response['SecurityGroups'][0]['GroupId']
        else:
            raise e

    # 3. Define User Data to automatically host the HTTP Server (Question 5 Preparation)
    user_data = """#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Assignment 4 HTTP Server is Running!</h1>" > /var/www/html/index.html
"""

    # 4. Launch the micro Amazon Linux instance
    ami_id = 'ami-06a83a7a581c729a9' # From direct_AMI_search_linux.py
    print(f"\nLaunching micro Amazon Linux instance with AMI {ami_id}...")
    
    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        UserData=user_data,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'A4-Amazon-Linux'}]
        }]
    )
    
    instance = instances[0]
    print(f"Instance ID {instance.id} created. Verifying running status...")
    
    # 5. Verify Running Status and Display Public DNS
    instance.wait_until_running()
    instance.reload()
    
    print("\n[SUCCESS] Instance is in 'running' status!")
    print(f"Public DNS Name: {instance.public_dns_name}")

if __name__ == "__main__":
    setup_and_launch()
