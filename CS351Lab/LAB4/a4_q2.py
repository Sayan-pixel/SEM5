# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 2

import boto3

def launch_ubuntu_instances():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    ec2_resource = boto3.resource('ec2', region_name='ap-south-1')
    
    key_name = 'assignment4-key'
    sg_name = 'assignment4-sg'
    
    # 1. Fetch Security Group ID
    try:
        response = ec2_client.describe_security_groups(GroupNames=[sg_name])
        sg_id = response['SecurityGroups'][0]['GroupId']
    except Exception as e:
        print(f"Error finding Security Group '{sg_name}'. Please run a4_q1.py first.")
        raise e

    # 2. Launch TWO micro Ubuntu instances
    ubuntu_ami_id = 'ami-07e5ce642bbc48c0d' # From direct_AMI_search_ubuntu.py
    print(f"Launching 2 micro Ubuntu instances with AMI {ubuntu_ami_id}...")
    
    instances = ec2_resource.create_instances(
        ImageId=ubuntu_ami_id,
        MinCount=2,
        MaxCount=2,
        InstanceType='t3.micro',
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'A4-Ubuntu'}]
        }]
    )
    
    # 3. Verify Running Status and Display Public DNS for both
    print("Instances created! Waiting for both to reach 'running' status...")
    for i, instance in enumerate(instances):
        instance.wait_until_running()
        instance.reload()
        print(f"\n[SUCCESS] Ubuntu Instance {i+1} ({instance.id}) is RUNNING!")
        print(f"Public DNS Name: {instance.public_dns_name}")

if __name__ == "__main__":
    launch_ubuntu_instances()
