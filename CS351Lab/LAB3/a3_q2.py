# Name: Sayan Shit
# Roll No: 2401179
# Assignment 3, Question 2

# This python script defines the startup script to install Apache and copy website files
# and saves it to a shell script file named 'startup.sh'

def create_startup_script():
    # Define the bash script content
    startup_script = """#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
# Copy the static website files from S3 to the Apache document root individually
cd /var/www/html/
aws s3 cp s3://sayan-assignment3-2026/website/index.html . --no-sign-request
aws s3 cp s3://sayan-assignment3-2026/website/style.css . --no-sign-request
aws s3 cp s3://sayan-assignment3-2026/website/script.js . --no-sign-request
"""
    # Write the content to a file
    with open("startup.sh", "w") as file:
        file.write(startup_script)
        
    print("Startup script successfully created and saved as 'startup.sh'.")

if __name__ == "__main__":
    create_startup_script()
