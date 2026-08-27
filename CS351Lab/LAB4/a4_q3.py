# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 3

import boto3

def list_running_instances():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    
    print("Fetching list of all running instances...")
    
    # Filter only instances that are in 'running' state
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    running_instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            
            # Find the Name tag if it exists
            name = "Unnamed"
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                        
            running_instances.append({
                'Name': name,
                'ID': instance_id,
                'Type': instance_type,
                'LaunchTime': str(instance['LaunchTime'])
            })
            
    if not running_instances:
        print("No running instances found.")
    else:
        print(f"Found {len(running_instances)} running instance(s):\n")
        print(f"{'Name':<20} | {'Instance ID':<20} | {'Type':<12} | {'Launch Time'}")
        print("-" * 80)
        for inst in running_instances:
            print(f"{inst['Name']:<20} | {inst['ID']:<20} | {inst['Type']:<12} | {inst['LaunchTime']}")

if __name__ == "__main__":
    list_running_instances()
