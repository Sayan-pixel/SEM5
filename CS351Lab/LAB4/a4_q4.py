# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 4

import boto3

def check_instance_health():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    
    print("Checking health status for all running instances...")
    
    # describe_instance_status returns health checks for running instances
    response = ec2_client.describe_instance_status()
    
    statuses = response.get('InstanceStatuses', [])
    
    if not statuses:
        print("No running instances found.")
    else:
        print(f"\nFound {len(statuses)} instance(s):")
        print(f"{'Instance ID':<20} | {'System Status':<15} | {'Instance Status'}")
        print("-" * 55)
        for status in statuses:
            instance_id = status['InstanceId']
            system_status = status['SystemStatus']['Status']
            instance_status = status['InstanceStatus']['Status']
            print(f"{instance_id:<20} | {system_status:<15} | {instance_status}")

if __name__ == "__main__":
    check_instance_health()
