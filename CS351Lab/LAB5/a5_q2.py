# Name: Sayan Shit
# Roll No: 2401179

import boto3
import time

def main():
    # 1. Initialize EC2 client
    ec2 = boto3.client('ec2', region_name='ap-south-1') 
    
    # 2. Read the startup script
    with open('startup.sh', 'r') as f:
        user_data_script = f.read()
        
    with open('base64.txt', 'r') as f:
        tar_b64 = f.read().replace('\r', '').strip()
        
    user_data_script = user_data_script.replace('WEBSITE_TAR_B64_PLACEHOLDER', tar_b64)
        
    print("Creating Security Group...")
    try:
        # Create a new security group
        sg_response = ec2.create_security_group(
            GroupName='portfolio-web-sg',
            Description='Security group for Lab 5 Portfolio Website'
        )
        security_group_id = sg_response['GroupId']
        print(f"Created Security Group ID: {security_group_id}")
        
        # Authorize HTTP (80) and SSH (22) inbound traffic
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
        print("Authorized inbound traffic on ports 80 and 22.")
    except ec2.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            print("Security Group 'portfolio-web-sg' already exists. Fetching its ID...")
            sg_info = ec2.describe_security_groups(GroupNames=['portfolio-web-sg'])
            security_group_id = sg_info['SecurityGroups'][0]['GroupId']
        else:
            print(f"Error creating security group: {e}")
            return
            
    print("Setting Ubuntu 22.04 AMI ID...")
    # Hardcoding AMI ID because your AWS IAM user lacks ssm:GetParameter permissions.
    # ami-03f4878755434977f is Ubuntu 22.04 LTS for ap-south-1
    ami_id = 'ami-03f4878755434977f'
    print(f"Using AMI ID: {ami_id}")
    
    print("Launching EC2 Instance...")
    try:
        instances = ec2.run_instances(
            ImageId=ami_id,
            InstanceType='t3.micro',
            SecurityGroupIds=[security_group_id],
            UserData=user_data_script,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Lab5-Portfolio-Instance'}]
                }
            ]
        )
        instance_id = instances['Instances'][0]['InstanceId']
        print(f"Successfully launched EC2 Instance with ID: {instance_id}")
    except Exception as e:
        print(f"Error launching instance: {e}")
        return
    
    print("Waiting for instance to enter 'running' state (this takes a minute)...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    
    # Retrieve instance information
    instance_info = ec2.describe_instances(InstanceIds=[instance_id])
    instance = instance_info['Reservations'][0]['Instances'][0]
    public_ip = instance.get('PublicIpAddress', 'N/A')
    public_dns = instance.get('PublicDnsName', 'N/A')
    
    print("\n--- INSTANCE IS RUNNING ---")
    print(f"Instance ID: {instance_id}")
    print(f"Public DNS:  {public_dns}")
    print(f"Public IP:   {public_ip}")
    print(f"Access Website: http://{public_ip}")
    
if __name__ == "__main__":
    main()
