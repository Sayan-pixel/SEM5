# CS351 - Lab 3: Python Boto3 AWS Automation (EC2 & S3) Guide

This document provides a complete guide for **Lab 3 (Python Boto3 Automation)**.

---

## Overview

- **Topics Covered**: AWS Boto3 SDK, S3 File Uploads, UserData Startup Scripts, Security Group Configuration (Port 80), EC2 Instance Provisioning (`t3.micro`), and Status Polling / Public DNS Retrieval.
- **Files**: `startup.sh`, `a3_q2.py`, `a3_q3.py`, `a3_q5.py`

---

## Workflow & Execution Steps

### Step 1: Install Boto3 and Configure AWS Credentials
```powershell
pip install boto3 awscli
aws configure
```
*(Enter Access Key ID, Secret Access Key, Default Region `us-east-1`, and Output format `json`).*

### Step 2: Upload Website to Amazon S3
Upload files from `portfolio/` to your S3 bucket using Boto3 or AWS CLI:
```powershell
aws s3 sync portfolio/ s3://your-s3-bucket-name/
```

### Step 3: Create UserData Startup Script (`startup.sh`)
The user-data script installs Apache (`httpd` or `apache2`), downloads website files from S3, and places them in `/var/www/html`:

```bash
#!/bin/bash
sudo apt update -y
sudo apt install -y apache2 awscli
sudo aws s3 sync s3://your-s3-bucket-name /var/www/html/ --no-sign-request
sudo systemctl restart apache2
```

### Step 4: Provision EC2 & Security Group via Boto3 Script (`a3_q3.py` & `a3_q5.py`)
Run the Python script to create security group (open Port 80), attach UserData script, launch instance, wait for `running` state, and return Public DNS:

```powershell
python a3_q5.py
```

### Step 5: Verification
Open the printed **Public DNS** or **Public IP** in your browser: `http://<ec2-public-dns>` to verify the Apache-hosted website.
