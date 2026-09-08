import boto3

ec2 = boto3.client('ec2', region_name='ap-south-1')
user_data = """#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y apache2-utils
# Run apache benchmark repeatedly
for i in {1..10}
do
   ab -n 500000 -c 200 http://65.0.103.183/
done
"""

print("Launching a temporary Load Generator EC2 instance in AWS...")
instances = ec2.run_instances(
    ImageId='ami-03f4878755434977f',
    InstanceType='t3.micro',
    MinCount=1,
    MaxCount=1,
    UserData=user_data,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'Temporary-Load-Generator'}]
        }
    ]
)

instance_id = instances['Instances'][0]['InstanceId']
print(f"Launched Load Generator Instance: {instance_id}")
print("This instance will blast the web server with high-speed traffic locally from within the AWS data center.")
print("The ScaleUp alarm should trigger in a few minutes!")
