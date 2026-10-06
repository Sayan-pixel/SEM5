# CS351 - Lab 6: Amazon RDS MySQL & Flask Feedback Application Guide

This document provides a guide for **Lab 6 (Amazon RDS MySQL Integration)**.

---

## Overview

- **Topics Covered**: Provisioning Amazon RDS (MySQL), Security Group DB ingress rule (Port 3306), Flask Web Application with MySQL integration (`pymysql` / `SQLAlchemy`), deploying Flask app on EC2, and storing feedback comments in RDS tables.
- **Files**: `create_rds.py`, `app.py`, `upload_helper.py`, `get_url.py`, `.env`, `website/`.

---

## Architecture & Execution Guide

### 1. Provision RDS MySQL Instance via Boto3 (`create_rds.py`)
Run `create_rds.py` to:
- Create Security Group allowing inbound MySQL port `3306` from EC2/IP.
- Call `boto3.client('rds').create_db_instance()` with parameters:
  - Engine: `mysql` (version `8.0`)
  - DB Instance Class: `db.t3.micro`
  - Master Username & Password: configured in script / `.env`
  - DB Name: `feedback_db`
- Poll until `DBInstanceStatus == 'available'`, then print the RDS Endpoint address.

```powershell
python create_rds.py
```

### 2. Configure Flask Application (`app.py` & `.env`)
Configure database environment variables in `.env`:
```ini
DB_HOST=<YOUR_RDS_ENDPOINT_ADDRESS>
DB_USER=admin
DB_PASSWORD=<YOUR_DB_PASSWORD>
DB_NAME=feedback_db
```

App features (`app.py`):
- Connects to MySQL using PyMySQL.
- Creates `feedback` table if not exists:
  ```sql
  CREATE TABLE IF NOT EXISTS feedback (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      email VARCHAR(100) NOT NULL,
      message TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
- Serves website UI (`index.html`) with Feedback form.
- `POST /submit_feedback`: Inserts user name, email, and message into RDS MySQL table.
- `GET /feedback`: Fetches and displays all submitted feedback.

### 3. Deploy Flask Application on AWS EC2
Deploy `app.py` and `website/` onto EC2:
```bash
sudo apt update && sudo apt install -y python3-pip python3-flask python3-pymysql
python3 app.py
```

### 4. Verification
Open EC2 Public IP / DNS in browser:
1. Submit a feedback message on the webpage.
2. Verify that the comment is saved in the Amazon RDS MySQL database table.
