# Name: Sayan Shit
# Roll No: 2401179
# Assignment 4, Question 5

import boto3
import urllib.request
import urllib.error

def verify_http_server():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    
    print("Finding the Amazon Linux instance to verify HTTP server...")
    
    # Filter for the Amazon Linux instance we created
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['A4-Amazon-Linux']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
            
    if not instances:
        print("Error: Could not find a running Amazon Linux instance.")
        return
        
    instance = instances[0]
    public_dns = instance.get('PublicDnsName')
    
    if not public_dns:
        print("Error: Instance does not have a public DNS name.")
        return
        
    url = f"http://{public_dns}"
    print(f"Connecting to {url} ...\n")
    
    try:
        # Send an HTTP GET request to verify the server is running
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode('utf-8').strip()
            status = response.getcode()
            print(f"[SUCCESS] HTTP Server is reachable! Status Code: {status}")
            print("Response Content:")
            print(html)
    except urllib.error.URLError as e:
        print(f"[FAILED] Could not connect to HTTP Server. Reason: {e.reason}")
        print("Note: If you just launched the instance, wait 60 seconds for Apache to finish installing and run this script again.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    verify_http_server()
