# Name: Sayan Shit
# Roll No: 2401179

import boto3
import time
import os

# Initialize EC2 resource and client
ec2_resource = boto3.resource('ec2', region_name='us-east-1')
ec2_client = boto3.client('ec2', region_name='us-east-1')

def create_security_group():
    """
    Question 4: Use a security group with port 80 open.
    Creates a security group in the default VPC and allows inbound HTTP traffic.
    """
    sg_name = 'lab3-web-sg-' + str(int(time.time()))
    print(f"Creating Security Group: {sg_name}")
    try:
        # Get the default VPC
        vpcs = ec2_client.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        
        # Create Security Group
        response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description='Security group for Lab 3 with port 80 open',
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        
        # Add Inbound rule to allow HTTP (Port 80) from anywhere
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        print(f"Security Group Created: {sg_id} (Port 80 open)")
        return sg_id
    except Exception as e:
        print(f"Error creating security group: {e}")
        return None

def launch_instance(sg_id):
    """
    Question 3: Create a Python program using boto3 to launch a t3.micro instance in EC2.
    Supply the startup script you created in the previous step.
    """
    script_path = r'e:\IIIT G\SEM_5\CS351Lab\LAB3\a3_q2_startup.sh'
    
    # Read the startup script
    try:
        with open(script_path, 'r') as file:
            startup_script = file.read()
            
        # Quick validation check to ensure user replaced the bucket name
        if 'YOUR_BUCKET_NAME' in startup_script:
            print("\n" + "!"*50)
            print("WARNING: You forgot to replace YOUR_BUCKET_NAME in a3_q2_startup.sh!")
            print("The instance will launch, but the website won't load.")
            print("!"*50 + "\n")
            
    except FileNotFoundError:
        print(f"Error: Startup script not found at {script_path}")
        return None

    print("Fetching the latest Amazon Linux 2 AMI...")
    try:
        # Find latest Amazon Linux 2 AMI
        response = ec2_client.describe_images(
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                {'Name': 'state', 'Values': ['available']}
            ],
            Owners=['amazon']
        )
        # Sort images by creation date
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        ami_id = images[0]['ImageId']
        print(f"Using AMI: {ami_id}")
    except Exception as e:
        print(f"Error fetching AMI: {e}")
        return None

    print("Launching EC2 instance...")
    try:
        instances = ec2_resource.create_instances(
            ImageId=ami_id,
            InstanceType='t3.micro',
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[sg_id],
            UserData=startup_script,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Lab3-WebServer'}]
                }
            ]
        )
        instance = instances[0]
        print(f"Instance {instance.id} launched successfully.")
        return instance
    except Exception as e:
        print(f"Error launching instance: {e}")
        return None

def check_status_and_get_dns(instance):
    """
    Question 5: Check the status of the newly launched instance and return 
    the public DNS address of the instance when the status changes to "running".
    """
    print(f"Waiting for instance {instance.id} to enter 'running' state...")
    
    # Wait until running
    instance.wait_until_running()
    
    # Reload the instance attributes to get the updated status and public DNS
    instance.reload()
    print("\nInstance is now RUNNING!")
    
    dns = instance.public_dns_name
    print(f"Public DNS Address: {dns}")
    
    # Question 6 reminder
    print("\n" + "="*50)
    print("Question 6: Verification")
    print("Please wait 2-3 minutes for the startup script to finish installing Apache and downloading files.")
    print(f"Then open http://{dns} in your browser to verify the website works.")
    print("="*50)

if __name__ == "__main__":
    # Question 4: Create Security Group
    security_group_id = create_security_group()
    
    if security_group_id:
        # Question 3: Launch instance with script
        ec2_instance = launch_instance(security_group_id)
        
        if ec2_instance:
            # Question 5: Check status and return DNS
            check_status_and_get_dns(ec2_instance)
