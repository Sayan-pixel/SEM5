# CS351 - Lab 7: AWS Elastic Beanstalk Application Deployment Guide

This document provides a complete guide for **Lab 7 (AWS Elastic Beanstalk Deployment)**.

---

## Overview

- **Topics Covered**: AWS Elastic Beanstalk (PaaS), Application Versioning, S3 Source Bundle Storage, Environment Creation (`64bit Amazon Linux 2023 v4.4.0 running Python 3.11`), Boto3 Elastic Beanstalk Client (`elasticbeanstalk`), and Automated Deployment.
- **Files**: `deploy.py`, `eb-app/application.py`, `eb-app/requirements.txt`, `lab7_app_clean.zip`.

---

## Application Structure (`eb-app`)

Elastic Beanstalk expects a WSGI entrypoint `application.py` with callable `application`:

### `application.py`
```python
from flask import Flask, render_template

application = Flask(__name__, static_folder='static', template_folder='templates')

@application.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)
```

### `requirements.txt`
```text
Flask==3.0.0
gunicorn==21.2.0
```

---

## Boto3 Elastic Beanstalk Deployment Script (`deploy.py`)

The automated Boto3 script performs the following 5 steps:

1. **Zip Application Source**:
   Compresses `application.py`, `requirements.txt`, `static/`, and `templates/` into `lab7_app.zip`.

2. **Upload Bundle to Amazon S3**:
   Uploads `lab7_app.zip` to Elastic Beanstalk default storage bucket (`s3://elasticbeanstalk-<region>-<account-id>`).

3. **Create Elastic Beanstalk Application**:
   Calls `eb_client.create_application(ApplicationName='CS351-Lab7-App')`.

4. **Create Application Version**:
   Calls `eb_client.create_application_version()` referencing the uploaded S3 zip bundle.

5. **Create & Launch Environment**:
   Calls `eb_client.create_environment()` with parameters:
   - `ApplicationName`: `CS351-Lab7-App`
   - `EnvironmentName`: `CS351-Lab7-Env`
   - `SolutionStackName`: `64bit Amazon Linux 2023 v4.4.0 running Python 3.11`
   - `OptionSettings`: Configures `aws:autoscaling:launchconfiguration` (`IamInstanceProfile` = `aws-elasticbeanstalk-ec2-role`).

6. **Poll Status & Retrieve CNAME Endpoint**:
   Polls `describe_environments()` until `Status == 'Ready'`, then prints the live CNAME URL (e.g. `http://CS351-Lab7-Env.us-east-1.elasticbeanstalk.com`).

---

## Execution Guide

Run the deployment script from your terminal:
```powershell
python deploy.py
```

Open the returned Elastic Beanstalk CNAME URL in your browser to verify your live deployed application.
