# Name: <Sayan Shit>
# Roll No: <2401179>

import boto3
import time

def launch_instance():
    # Initialize the EC2 resource
    ec2 = boto3.resource('ec2', region_name='ap-south-1') # Change region if needed

    # Read the startup script
    try:
        with open('startup.sh', 'r') as file:
            user_data_script = file.read()
    except FileNotFoundError:
        print("Error: startup.sh file not found.")
        return

    print("Launching EC2 instance...")
    
    # Launch the EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-0f48d8eda3141f50a', # Amazon Linux 2023 AMI in ap-south-1
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro', # As per assignment
        KeyName='assignment3-key', # Your AWS Key Pair name
        SecurityGroupIds=['sg-0566b365ce7fcfe1b'], # Your Security Group ID (assignment3-sg)
        UserData=user_data_script
    )

    instance = instances[0]
    
    print(f"Instance {instance.id} created. Waiting for it to enter 'running' state...")
    
    # Wait until the instance is running (Question 5)
    instance.wait_until_running()
    
    # Reload the instance attributes to get the public DNS
    instance.reload()
    
    print(f"Instance is now running!")
    print(f"Public DNS Address: {instance.public_dns_name}")
    print(f"You can verify the website at: http://{instance.public_dns_name}")

if __name__ == "__main__":
    launch_instance()
