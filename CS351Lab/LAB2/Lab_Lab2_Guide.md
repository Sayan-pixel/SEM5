# CS351 - Lab 2: AWS EC2 & S3 Static Website Hosting Guide

This document provides a step-by-step walkthrough for completing **Lab 2 (AWS EC2 & S3)**.

---

## Overview

- **Topics Covered**: AWS Console, EC2 Instance Launch (`t3.micro`), SSH/PuTTY login, SCP file transfer, S3 Bucket creation, S3 Static Website Hosting, and Bucket Policy access restriction.
- **Project Folder**: `portfolio/`

---

## Step-by-Step Execution Guide

### Part 1: AWS EC2 Instance Setup

1. **Launch EC2 Instance**:
   - Log into AWS Management Console -> Go to **EC2**.
   - Click **Launch Instance**.
   - **Name**: `Lab2-EC2-Instance`
   - **AMI**: Ubuntu Server 22.04 LTS or Amazon Linux 2.
   - **Instance Type**: `t3.micro` (or `t2.micro` free tier).
   - **Key Pair**: Create or select `.pem` key pair (e.g., `lab2-key.pem`).
   - **Network Settings**: Allow SSH (`22`) and HTTP (`80`).

2. **Connect via SSH / PuTTY**:
   - **OpenSSH (Terminal/PowerShell)**:
     ```powershell
     ssh -i "path/to/lab2-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
     ```
   - **PuTTY**: Convert `.pem` to `.ppk` using PuTTYgen -> Host Name: `ubuntu@<PUBLIC_IP>` -> Connection -> SSH -> Auth -> Browse `.ppk`.

3. **Transfer Files via SCP**:
   ```powershell
   scp -i "path/to/lab2-key.pem" Hello.txt ubuntu@<YOUR_EC2_PUBLIC_IP>:/home/ubuntu/
   ```

---

### Part 2: Amazon S3 Static Website Hosting & Access Control

1. **Create S3 Bucket**:
   - Go to **S3** in AWS Console -> Click **Create Bucket**.
   - **Bucket Name**: `cs351-lab2-portfolio-<your-name>` (must be globally unique).
   - **Block Public Access**: Uncheck "Block *all* public access" (acknowledge warning).

2. **Create Folders**:
   - Inside the S3 bucket, create two folders:
     - `website/`
     - `personal/`

3. **Upload Static Website**:
   - Upload contents of `portfolio/` (e.g. `index.html`, `css/`, `js/`) into the `website/` folder.

4. **Enable Static Website Hosting**:
   - Go to Bucket -> **Properties** tab -> Scroll to **Static website hosting** -> Click **Edit**.
   - Select **Enable** -> Index document: `website/index.html`.
   - Save changes and note the bucket website endpoint URL.

5. **Bucket Policy & Access Control**:
   - Go to **Permissions** tab -> **Bucket Policy** -> Add public read policy for `website/*`:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadForWebsite",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::cs351-lab2-portfolio-<your-name>/website/*"
       }
     ]
   }
   ```
   - For `personal/` folder access restriction to a specific user (IAM ARN), add an explicit statement granting access only to specified friend's IAM User ARN.
