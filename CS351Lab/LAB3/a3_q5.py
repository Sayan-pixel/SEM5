# Name: Sayan Shit
# Roll No: 2401179
# Assignment 3, Question 5

import boto3
import sys

def check_status_and_get_dns(instance_id):
    """
    Checks the status of the newly launched instance and returns the public DNS 
    address when the status changes to 'running'.
    """
    # Initialize the EC2 resource
    ec2 = boto3.resource('ec2', region_name='ap-south-1')
    
    # Get the instance object using the ID
    instance = ec2.Instance(instance_id)
    
    print(f"Checking status for instance '{instance_id}'...")
    print("Waiting for the status to change to 'running'...")
    
    # Wait until the instance is in the 'running' state
    instance.wait_until_running()
    
    # Reload the instance attributes to fetch the public DNS
    instance.reload()
    
    print("Instance status is now 'running'.")
    print(f"Public DNS Address: http://{instance.public_dns_name}")
    print("Open this URL in your browser to verify the static website (Question 6).")

if __name__ == "__main__":
    # --- PASTE YOUR INSTANCE ID HERE ---
    # Replace the placeholder below with the Instance ID you got from running a3_q3.py
    INSTANCE_ID = 'i-0d80479a0baabc836' 
    
    if INSTANCE_ID == 'i-0abcd1234efgh5678':
        print("Error: Please edit a3_q5.py and replace INSTANCE_ID with your actual Instance ID from Q3.")
        sys.exit(1)
        
    check_status_and_get_dns(INSTANCE_ID)
