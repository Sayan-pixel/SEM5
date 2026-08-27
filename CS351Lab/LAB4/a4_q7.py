# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 7

import boto3

def terminate_all_instances():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    ec2_resource = boto3.resource('ec2', region_name='ap-south-1')
    
    print("Finding all stopped or running instances to terminate...")
    
    # Filter for all running, stopping, or stopped instances
    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'stopping']}]
    )
    
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    if not instance_ids:
        print("No instances found to terminate.")
        return
        
    print(f"Terminating the following {len(instance_ids)} instance(s): {', '.join(instance_ids)}")
    
    # Terminate the instances
    ec2_client.terminate_instances(InstanceIds=instance_ids)
    
    print("Command sent! Waiting for instances to enter 'terminated' state (this may take a minute)...")
    
    # Wait for all to terminate
    for instance_id in instance_ids:
        instance = ec2_resource.Instance(instance_id)
        instance.wait_until_terminated()
        print(f"Instance {instance_id} is now TERMINATED.")
        
    print("\n[SUCCESS] All instances have been successfully terminated.")

if __name__ == "__main__":
    terminate_all_instances()
