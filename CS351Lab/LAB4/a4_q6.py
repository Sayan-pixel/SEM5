# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 6

import boto3

def stop_all_instances():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    ec2_resource = boto3.resource('ec2', region_name='ap-south-1')
    
    print("Finding all running instances to stop...")
    
    # Filter for all running instances
    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    if not instance_ids:
        print("No running instances found to stop.")
        return
        
    print(f"Stopping the following {len(instance_ids)} instance(s): {', '.join(instance_ids)}")
    
    # Stop the instances
    ec2_client.stop_instances(InstanceIds=instance_ids)
    
    print("Command sent! Waiting for instances to enter 'stopped' state (this may take a minute)...")
    
    # Wait for all to stop
    for instance_id in instance_ids:
        instance = ec2_resource.Instance(instance_id)
        instance.wait_until_stopped()
        print(f"Instance {instance_id} is now STOPPED.")
        
    print("\n[SUCCESS] All instances have been successfully stopped.")

if __name__ == "__main__":
    stop_all_instances()
