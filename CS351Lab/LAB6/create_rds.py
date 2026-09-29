# Name: Sayan Shit
# Roll No: 2401179
# CS351 Lab Assignment 6 - RDS

import boto3
import time
import pymysql
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
def create_rds_instance():
    """
    Creates an RDS MySQL instance and a corresponding Security Group with port 3306 open.
    Outputs the Endpoint and Security Group details.
    """
    # Create EC2 client for Security Group
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    
    # Create RDS client
    rds_client = boto3.client('rds', region_name='ap-south-1')

    print("Creating Security Group for RDS...")
    # Get default VPC
    vpcs = ec2_client.describe_vpcs()
    vpc_id = vpcs['Vpcs'][0]['VpcId']
    
    # Create security group
    sg_name = 'rds-feedback-sg'
    try:
        sg_response = ec2_client.create_security_group(
            GroupName=sg_name,
            Description='Security group for Feedback RDS instance',
            VpcId=vpc_id
        )
        sg_id = sg_response['GroupId']
        print(f"Security Group Created: {sg_id}")
        
        # Add inbound rule for MySQL (Port 3306) from anywhere
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3306,
                    'ToPort': 3306,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        print("Inbound rule for port 3306 added.")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            print("Security Group already exists. Fetching existing SG...")
            sgs = ec2_client.describe_security_groups(GroupNames=[sg_name])
            sg_id = sgs['SecurityGroups'][0]['GroupId']
        else:
            print(f"Error creating security group: {e}")
            return

    print("Creating RDS MySQL Instance...")
    try:
        try:
            response = rds_client.create_db_instance(
                DBInstanceIdentifier='feedback-db-instance',
                AllocatedStorage=20,
                DBInstanceClass='db.t3.micro',
                Engine='mysql',
                MasterUsername=DB_USER,
                MasterUserPassword=DB_PASSWORD,
                VpcSecurityGroupIds=[sg_id],
                PubliclyAccessible=True,
                DBName=DB_NAME
            )
            print("RDS Instance is being created. This will take a few minutes...")
        except rds_client.exceptions.DBInstanceAlreadyExistsFault:
            print("RDS Instance already exists. Skipping creation...")
        
        # Wait until the instance is available
        waiter = rds_client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier='feedback-db-instance')
        
        # Fetch the endpoint
        instances = rds_client.describe_db_instances(DBInstanceIdentifier='feedback-db-instance')
        endpoint = instances['DBInstances'][0]['Endpoint']['Address']
        print(f"\n======================================")
        print(f"RDS Instance is available!")
        print(f"Endpoint: {endpoint}")
        print(f"Security Group ID: {sg_id}")
        print(f"======================================\n")
        
        # Connect to MySQL and create the table
        print("Connecting to RDS to create the feedbacks table...")
        
        # Give RDS some time to be fully ready for connections
        # Implement a retry loop because it can take a few minutes after "available" state
        max_retries = 12
        connection = None
        for attempt in range(max_retries):
            try:
                print(f"Attempting to connect to the database (Attempt {attempt + 1}/{max_retries})...")
                connection = pymysql.connect(
                    host=endpoint,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=10
                )
                print("Successfully connected to RDS!")
                break
            except pymysql.err.OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"Connection failed: {e}. Retrying in 15 seconds...")
                    time.sleep(15)
                else:
                    raise Exception(f"Could not connect to the database after {max_retries} attempts. {e}")
        
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
        connection.commit()
        connection.close()
        print("Feedback table created successfully in RDS!")
        
    except Exception as e:
        print(f"Error creating RDS instance or table: {e}")

if __name__ == "__main__":
    create_rds_instance()
