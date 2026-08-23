#!/bin/bash
# Install Apache web server
yum update -y
yum install -y httpd

# Start the web server and ensure it starts on boot
systemctl start httpd
systemctl enable httpd

# --- IMPORTANT ---
# Replace YOUR_BUCKET_NAME with the actual bucket name printed when you ran a3_q1.py
BUCKET_NAME="YOUR_BUCKET_NAME"

# Navigate to web server root directory
cd /var/www/html/

# Download the website files from the public S3 bucket
wget https://${BUCKET_NAME}.s3.amazonaws.com/index.html
wget https://${BUCKET_NAME}.s3.amazonaws.com/style.css
wget https://${BUCKET_NAME}.s3.amazonaws.com/script.js

# Restart Apache to serve new files
systemctl restart httpd
