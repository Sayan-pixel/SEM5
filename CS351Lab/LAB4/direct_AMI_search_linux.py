import boto3

ec2_client = boto3.client("ec2", region_name="ap-south-1")

# Filter public images owned by Amazon matching the AL2023 naming pattern
response = ec2_client.describe_images(
    Owners=["amazon"],
    Filters=[
        {"Name": "name", "Values": ["al2023-ami-2023.*-x86_64"]},
        {"Name": "state", "Values": ["available"]},
    ],
)

# Sort the images by CreationDate to get the newest release
latest_ami = sorted(
    response["Images"], key=lambda x: x["CreationDate"], reverse=True
)[0]

print(f"AMI ID: {latest_ami['ImageId']}")
print(f"AMI Name: {latest_ami['Name']}")
print(f"Creation Date: {latest_ami['CreationDate']}")

# Save these AMI ID, AMI Name, Creation Date within the same folder named LAB4 as a txt file format
with open("ami_details_linux.txt", "w") as file:
    file.write(f"AMI ID: {latest_ami['ImageId']}\n")
    file.write(f"AMI Name: {latest_ami['Name']}\n")
    file.write(f"Creation Date: {latest_ami['CreationDate']}\n")
    
print("Successfully saved AMI details to 'ami_details_linux.txt'.")