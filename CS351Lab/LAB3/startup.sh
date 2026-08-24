#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
# Copy the static website files from S3 to the Apache document root individually
cd /var/www/html/
aws s3 cp s3://sayan-assignment3-2026/website/index.html . --no-sign-request
aws s3 cp s3://sayan-assignment3-2026/website/style.css . --no-sign-request
aws s3 cp s3://sayan-assignment3-2026/website/script.js . --no-sign-request
