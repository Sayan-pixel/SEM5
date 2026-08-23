import boto3

# Initialize AWS resources
ec2_client = boto3.client('ec2', region_name='us-east-1')
ec2_resource = boto3.resource('ec2', region_name='us-east-1')
s3_resource = boto3.resource('s3', region_name='us-east-1')

def cleanup_s3_buckets():
    print("--- Cleaning up S3 Buckets ---")
    for bucket in s3_resource.buckets.all():
        if bucket.name.startswith("sayan-2401179-lab3-bucket"):
            print(f"Deleting contents and bucket: {bucket.name}")
            try:
                # S3 buckets must be empty before they can be deleted
                bucket.objects.all().delete()
                bucket.delete()
                print(f"Successfully deleted {bucket.name}")
            except Exception as e:
                print(f"Failed to delete {bucket.name}: {e}")

def cleanup_ec2_instances():
    print("\n--- Cleaning up EC2 Instances ---")
    instances = ec2_resource.instances.filter(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['Lab3-WebServer']},
            {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopped']}
        ]
    )
    
    instance_ids = [instance.id for instance in instances]
    
    if instance_ids:
        print(f"Terminating instances: {instance_ids}")
        try:
            ec2_resource.instances.filter(InstanceIds=instance_ids).terminate()
            print("Termination request sent successfully. (It may take a few minutes to fully terminate)")
            
            # Wait for instances to terminate so we can safely delete the security group later
            print("Waiting for instances to terminate completely...")
            waiter = ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=instance_ids)
            print("Instances terminated!")
            
        except Exception as e:
            print(f"Failed to terminate instances: {e}")
    else:
        print("No 'Lab3-WebServer' instances found to terminate.")

def cleanup_security_groups():
    print("\n--- Cleaning up Security Groups ---")
    try:
        response = ec2_client.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['lab3-web-sg-*']}]
        )
        
        for sg in response['SecurityGroups']:
            sg_id = sg['GroupId']
            sg_name = sg['GroupName']
            print(f"Deleting Security Group: {sg_name} ({sg_id})")
            try:
                ec2_client.delete_security_group(GroupId=sg_id)
                print(f"Successfully deleted {sg_name}")
            except Exception as e:
                print(f"Failed to delete {sg_name}: {e} (This can happen if instances are still terminating)")
    except Exception as e:
        print(f"Error fetching security groups: {e}")

if __name__ == "__main__":
    print("Starting AWS Cleanup Process...\n")
    cleanup_ec2_instances()
    cleanup_security_groups()
    cleanup_s3_buckets()
    print("\nCleanup Complete!")
