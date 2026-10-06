# CS351 - Lab 4: Boto3 Multi-Instance Automation & Instance Lifecycle Guide

This document provides a guide for **Lab 4 (Boto3 Multi-Instance Lifecycle Automation)**.

---

## Overview

- **Topics Covered**: Querying AMIs (Amazon Linux & Ubuntu), launching single/multiple EC2 instances via Boto3, checking instance status and health, hosting HTTP server via UserData, stopping instances, and terminating instances.
- **Files**: `a4_q0.py` through `a4_q7.py`, `direct_AMI_search_linux.py`, `direct_AMI_search_ubuntu.py`.

---

## Script Breakdown & Execution Order

### 1. AMI Search Scripts
- `direct_AMI_search_linux.py`: Finds latest Amazon Linux 2 AMI ID.
- `direct_AMI_search_ubuntu.py`: Finds latest Ubuntu 22.04 LTS AMI ID.
- Run:
  ```powershell
  python direct_AMI_search_linux.py
  python direct_AMI_search_ubuntu.py
  ```

### 2. Question 1 (`a4_q1.py`): Launch Amazon Linux Instance
Launches 1 `t3.micro` Amazon Linux instance, polls until state is `running`, and displays Public DNS.
```powershell
python a4_q1.py
```

### 3. Question 2 (`a4_q2.py`): Launch Two Ubuntu Instances
Launches 2 `t3.micro` Ubuntu instances, waits for `running` status, and prints Public DNS names.
```powershell
python a4_q2.py
```

### 4. Question 3 (`a4_q3.py`): List Running Instances
Queries AWS EC2 for all instances currently in `running` state.
```powershell
python a4_q3.py
```

### 5. Question 4 (`a4_q4.py`): Check Instance Health Status
Retrieves system status and instance status checks using `describe_instance_status()`.
```powershell
python a4_q4.py
```

### 6. Question 5 (`a4_q5.py`): Host HTTP Server
Launches instance with HTTP web server enabled via UserData script.
```powershell
python a4_q5.py
```

### 7. Question 6 (`a4_q6.py`): Stop Instances
Stops active running EC2 instances (`stop_instances()`).
```powershell
python a4_q6.py
```

### 8. Question 7 (`a4_q7.py`): Terminate Instances
Terminates EC2 instances (`terminate_instances()`) to prevent unwanted AWS charges.
```powershell
python a4_q7.py
```
