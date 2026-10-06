# Name: Sayan Shit
# Roll No: 2401179
# CS351 Lab Assignment 7 - AWS Elastic Beanstalk Deployment

import boto3
import time
import uuid

def upload_zip_to_s3(s3_client, bucket_name, file_path, object_name):

    print(f"Checking/Creating S3 bucket: {bucket_name}...")
    try:
        # ap-south-1 requires LocationConstraint
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'}
        )
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print("Bucket already exists and is owned by you. Proceeding...")
    except Exception as e:
        print(f"Bucket creation exception (might already exist): {e}")

    print(f"Uploading {file_path} to S3 bucket {bucket_name} as {object_name}...")
    s3_client.upload_file(file_path, bucket_name, object_name)
    print("Upload complete!")

def create_eb_application(eb_client, app_name):

    print(f"Creating Elastic Beanstalk Application: {app_name}...")
    try:
        eb_client.create_application(
            ApplicationName=app_name,
            Description='My Personal Website deployed via Boto3'
        )
        print("Application created successfully.")
    except Exception as e:
        print(f"Application may already exist: {e}")

def create_eb_app_version(eb_client, app_name, version_label, bucket_name, object_name):

    print(f"Creating Application Version: {version_label}...")
    try:
        eb_client.create_application_version(
            ApplicationName=app_name,
            VersionLabel=version_label,
            SourceBundle={
                'S3Bucket': bucket_name,
                'S3Key': object_name
            },
            Process=False
        )
        print("Application version created.")
    except Exception as e:
        print(f"Application version creation failed (might already exist): {e}")

def deploy_eb_environment(eb_client, app_name, env_name, version_label):

    print("Finding the correct Python 3.12 Solution Stack...")
    stacks = eb_client.list_available_solution_stacks()['SolutionStacks']
    # Find a Python stack (Amazon Linux 2023 is preferred, but fallback to any Python 3 stack)
    python_stacks = [s for s in stacks if 'Python' in s]
    if not python_stacks:
        raise Exception("No Python solution stacks found!")
    
    # Try to find Python 3.12 or latest Python 3 on AL2023
    python_stack = next((s for s in python_stacks if 'Python 3.12' in s), python_stacks[0])
    print(f"Using Solution Stack: {python_stack}")

    print(f"Creating Environment: {env_name}...")
    try:
        response = eb_client.create_environment(
            ApplicationName=app_name,
            EnvironmentName=env_name,
            VersionLabel=version_label,
            SolutionStackName=python_stack,
            OptionSettings=[
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'IamInstanceProfile',
                    'Value': 'NewRole_AWSElasticBeanstalkWebTier' # Reusing the role from previous manual lab
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'EnvironmentType',
                    'Value': 'SingleInstance'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'InstanceType',
                    'Value': 't3.micro'
                }
            ]
        )
        print(f"Environment creation initiated. Environment ID: {response['EnvironmentId']}")
        cname = response.get('CNAME', 'Pending (Check AWS Console for URL)')
        print(f"Environment URL: {cname}")
        print("\nPlease wait a few minutes for the environment to launch.")
        print("You can check the AWS Console to see the live status.")
    except Exception as e:
        print(f"Error creating environment: {e}")

def main():
    # 1. Configuration Variables
    # Adding a random UUID to bucket to ensure global uniqueness
    unique_id = str(uuid.uuid4())[:8]
    bucket_name = f"sayan-2401179-eb-bucket-{unique_id}"
    app_name = "Boto3-WebApp-Sayan"
    env_name = "Boto3-WebApp-Env"
    version_label = "v1-boto3"
    file_path = r"e:\IIIT G\SEM_5\CS351Lab\LAB7\lab7_app_clean.zip"
    object_name = "lab7_app_clean.zip"

    # 2. Initialize Boto3 Clients
    s3_client = boto3.client('s3', region_name='ap-south-1')
    eb_client = boto3.client('elasticbeanstalk', region_name='ap-south-1')

    # 3. Execute Deployment Steps
    upload_zip_to_s3(s3_client, bucket_name, file_path, object_name)
    create_eb_application(eb_client, app_name)
    create_eb_app_version(eb_client, app_name, version_label, bucket_name, object_name)
    deploy_eb_environment(eb_client, app_name, env_name, version_label)

if __name__ == "__main__":
    main()
