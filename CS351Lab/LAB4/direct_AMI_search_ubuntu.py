import boto3

ec2_client = boto3.client("ec2", region_name="ap-south-1")

# 099720109477 is Canonical's official AWS account ID
response = ec2_client.describe_images(
    Owners=["099720109477"],
    Filters=[
        {
            "Name": "name",
            "Values": [
                "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
            ],
        },
        {"Name": "state", "Values": ["available"]},
    ],
)

# Sort by CreationDate descending to select the newest build
latest_ami = sorted(
    response["Images"], key=lambda x: x["CreationDate"], reverse=True
)[0]

print(f"AMI ID: {latest_ami['ImageId']}")
print(f"AMI Name: {latest_ami['Name']}")
print(f"Creation Date: {latest_ami['CreationDate']}")

# Save these AMI ID, AMI Name, Creation Date within the same folder named LAB4 as a txt file format
with open("ami_details_ubuntu.txt", "w") as file:
    file.write(f"AMI ID: {latest_ami['ImageId']}\n")
    file.write(f"AMI Name: {latest_ami['Name']}\n")
    file.write(f"Creation Date: {latest_ami['CreationDate']}\n")
    
print("Successfully saved Ubuntu AMI details to 'ami_details_ubuntu.txt'.")