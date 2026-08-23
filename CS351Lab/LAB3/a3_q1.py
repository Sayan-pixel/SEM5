# Name: Sayan Shit
# Roll No: 2401179

import boto3
import json
import os
import time

# Initialize S3 client (Make sure AWS CLI is configured with your credentials)
s3_client = boto3.client('s3', region_name='us-east-1')

# Define a unique bucket name using your roll number and current timestamp
bucket_name = 'sayan-2401179-lab3-bucket-' + str(int(time.time()))

# The path to your LAB2 portfolio website
portfolio_dir = r'e:\IIIT G\SEM_5\CS351Lab\LAB2\portfolio'

def create_s3_bucket(bucket_name):
    """
    Creates an S3 bucket and makes it publicly readable.
    """
    print(f"Creating bucket: {bucket_name}")
    try:
        # Create bucket (us-east-1 does not require a LocationConstraint)
        s3_client.create_bucket(Bucket=bucket_name)
        print("Bucket created successfully.")
        
        # Disable Block Public Access to allow the bucket policy to work
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("Removed Block Public Access.")
        
        # Add a bucket policy to allow public read access to all objects in the bucket
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("Bucket policy updated to allow public read.")
        
    except Exception as e:
        print(f"Error creating bucket or applying policy: {e}")

def upload_files_to_s3(bucket_name, directory):
    """
    Uploads all files from the specified directory to the S3 bucket.
    """
    print(f"Uploading files from {directory} to S3 bucket {bucket_name}...")
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            try:
                # Set content type appropriately so it serves correctly on the web
                content_type = 'text/plain'
                if filename.endswith('.html'):
                    content_type = 'text/html'
                elif filename.endswith('.css'):
                    content_type = 'text/css'
                elif filename.endswith('.js'):
                    content_type = 'application/javascript'
                    
                s3_client.upload_file(
                    filepath, 
                    bucket_name, 
                    filename,
                    ExtraArgs={'ContentType': content_type}
                )
                print(f"Uploaded {filename}")
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")

if __name__ == "__main__":
    # Create the bucket
    create_s3_bucket(bucket_name)
    
    # Upload website files
    upload_files_to_s3(bucket_name, portfolio_dir)
    
    print("\n" + "="*50)
    print(f"SUCCESS! Please copy your bucket name: {bucket_name}")
    print("IMPORTANT: You must paste this bucket name into 'a3_q2_startup.sh' before running a3_q3.py")
    print("="*50)
