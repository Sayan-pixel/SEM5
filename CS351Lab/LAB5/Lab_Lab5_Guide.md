# CS351 - Lab 5: AWS Auto Scaling Group (ASG) & CloudWatch Alarms Guide

This document provides a guide for **Lab 5 (Auto Scaling & CloudWatch Monitoring)**.

---

## Overview

- **Topics Covered**: Dynamic EC2 metadata injection, Launch Templates, Auto Scaling Groups (ASG), CloudWatch Metric Alarms (CPU Utilization), Scale-up & Scale-down Policies, and Stress Testing.
- **Files**: `startup.sh`, `a5_q2.py`, `a5_q3.py`, `stress_test.py`, `load_generator.py`.

---

## Architecture & Workflow

1. **Part 1: Dynamic Metadata Startup Script (`startup.sh`)**:
   - Fetches Instance ID via IMDSv2:
     ```bash
     TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
     INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token-ttl-seconds: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
     ```
   - Injects `$INSTANCE_ID` dynamically into the HTML homepage `/var/www/html/index.html`.

2. **Part 2: Boto3 Instance Automation (`a5_q2.py`)**:
   - Creates Security Group (Port 80 allowed).
   - Launches single EC2 instance with `startup.sh`.
   - Returns Instance ID and Public DNS.

3. **Part 3: Auto Scaling Group & CloudWatch Alarms (`a5_q3.py`)**:
   - **Launch Template**: Configured with Ubuntu AMI, `t3.micro`, security group, and `startup.sh`.
   - **Auto Scaling Group**:
     - Region/AZ: `ap-south-1a`
     - Min Size: `1`, Max Size: `3`, Desired Capacity: `1`
   - **Scaling Policies**:
     - `ScaleOutPolicy`: StepScaling / SimpleScaling -> Add +1 instance.
     - `ScaleInPolicy`: StepScaling / SimpleScaling -> Remove -1 instance.
   - **CloudWatch Alarms**:
     - `HighCPUAlarm`: Triggers ScaleOut when `CPUUtilization >= 20%` for 2 minutes.
     - `LowCPUAlarm`: Triggers ScaleIn when `CPUUtilization <= 30%` for 2 minutes.

4. **Testing Auto Scaling**:
   - **Apply Load**: Run `stress_test.py` or `load_generator.py` on the instance or hit endpoint with concurrent HTTP requests.
   - **Verify Scale-up**: Watch CloudWatch alarm switch to `ALARM` state -> ASG launches a 2nd instance -> Refresh website to see different Instance IDs on the homepage.
   - **Remove Load**: Stop stress test -> CPU drops -> Scale-in policy terminates extra instance back down to 1.
