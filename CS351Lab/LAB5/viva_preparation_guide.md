# Comprehensive Viva Preparation Guide for AWS EC2, Auto Scaling, and CloudWatch

This document serves as an extended and detailed preparation guide for your Lab 5 Viva, based on the implementation of EC2 instances, automation using `boto3`, Auto Scaling Groups, and CloudWatch.

---


## Topic 1: Boto3 and AWS Automation

**What is Boto3?**
Boto3 is the official Amazon Web Services (AWS) SDK for Python. It allows Python developers to write software that makes use of services like Amazon S3, Amazon EC2, CloudWatch, etc., through programmatic API calls instead of clicking through the AWS Management Console. Under the hood, Boto3 makes HTTP/HTTPS requests to AWS API endpoints.

**Clients vs. Resources in Boto3**
In `a5_q2.py` and `a5_q3.py`, you used `boto3.client('ec2')`. 
- A **client** provides a low-level, one-to-one mapping with the underlying AWS API. It returns raw dictionary responses exactly as the AWS service provides them. It requires you to parse the JSON-like dictionaries.
- A **resource** provides a higher-level, object-oriented API (e.g., returning instance objects like `ec2.Instance(id)`), making it more Pythonic and easier to work with, though you mostly stuck with clients in this lab for granular control.

**Security Groups (`portfolio-web-sg`)**
- **What is it?** A Security Group acts as a stateful virtual firewall that controls inbound and outbound traffic at the instance level. By default, AWS denies all inbound traffic.
- **Rules applied:** You opened Port 80 (TCP) for HTTP (web traffic) and Port 22 (TCP) for SSH. 
- **What is `0.0.0.0/0`?** It's a CIDR (Classless Inter-Domain Routing) block that represents "all IPv4 addresses." This means anyone on the internet can access the website on port 80. While okay for port 80, opening port 22 to `0.0.0.0/0` is generally considered a security risk in production (it should be restricted to your specific IP).

---

## Topic 2: EC2 Instance Initialization & UserData

**What is UserData?**
When you launch an EC2 instance, you can pass user data to it. This data takes the form of a shell script (`startup.sh` in your case) that the `cloud-init` service executes with `root` privileges exactly once when the instance boots up for the very first time. It is heavily used for bootstrapping instances.

**Key Operations in `startup.sh`:**
1. **Installs Apache2:** The script runs `apt-get update -y` and `apt-get install -y apache2` to update repositories and set up an HTTP web server. `systemctl` is then used to start and enable it so it survives reboots.
2. **AWS Instance Metadata Service (IMDS):** 
   - IMDS runs on a link-local IP address: `169.254.169.254`. It allows the instance to query data about itself (like instance ID, region, public IP) without needing IAM API permissions.
   - You used it to fetch the `instance-id`. 
   - *Viva Tip:* Notice that the script gets a token first: `curl -X PUT ... /latest/api/token`. This is **IMDSv2**, which is more secure than v1. IMDSv2 requires session tokens, protecting the instance against Server-Side Request Forgery (SSRF) vulnerabilities where an attacker might try to trick your web application into querying the metadata service.
3. **Deploying the Website:** In `a5_q2.py`, you read a `base64.txt` file (your compressed website), replaced a placeholder in the shell script with this base64 string, and then decoded it on the instance: `base64 -di ...`. 
   - *Why base64?* Shell scripts are plain text. You cannot easily paste binary files (like images or tarballs) directly into them. Base64 encodes binary data into safe ASCII text, allowing you to embed entire websites directly inside the UserData string without needing to download them from S3 or GitHub during boot.

**Waiters in Boto3**
In `a5_q2.py`, you used `waiter.wait(InstanceIds=[instance_id])`. Waiters abstract away the complexity of polling the AWS API. Instead of writing a `while` loop that sleeps and checks the status of the instance, the waiter automatically handles the polling and pauses the script's execution until the resource reaches the desired state (in this case, `running`).

---

## Topic 3: Launch Templates & Auto Scaling Groups (ASG)

*This is the core of `a5_q3.py`.*

**Launch Templates**
Before an ASG can create new instances, it needs to know *what* to create. The Launch Template contains all the configuration details: the AMI ID (Ubuntu 22.04), instance type (`t3.micro`), Security Group, and the base64-encoded UserData. 
- *Why use them over Launch Configurations?* Launch Templates are the modern AWS standard. They support versioning (allowing you to update the template without recreating it) and advanced features like mixing instance types or specifying Spot instances.

**Auto Scaling Group (ASG)**
An ASG contains a collection of EC2 instances that are treated as a logical grouping for the purposes of automatic scaling and management.
- **MinSize (1):** The absolute minimum number of instances. The ASG will never let the instance count drop below this, even if the CPU is at 0%. This ensures your application is never completely offline.
- **MaxSize (3):** The hard limit. The ASG will not scale out beyond 3 instances, preventing run-away cloud bills and resource exhaustion.
- **DesiredCapacity (1):** What the ASG should start with initially.
- **Availability Zones (AZs):** You deployed in `ap-south-1a` and `ap-south-1b`. AWS Regions (like Mumbai `ap-south-1`) are made of multiple isolated data centers called AZs. Spanning your ASG across AZs provides High Availability (HA). If one AWS data center loses power, your ASG can automatically spin up instances in the surviving zone.

---

## Topic 4: CloudWatch Alarms and Scaling Policies

For the ASG to scale dynamically, it needs metrics and rules.

**Scaling Policies (Simple Scaling)**
- **Scale Out Policy:** Instructs the ASG to add exactly 1 instance (`ScalingAdjustment=1`, `ChangeInCapacity`).
- **Scale In Policy:** Instructs the ASG to remove 1 instance (`ScalingAdjustment=-1`).
Both have a **Cooldown** of 60 seconds. A cooldown period gives the newly launched instance time to boot up and start serving traffic before CloudWatch evaluates the metrics again. Without it, CloudWatch might keep triggering alarms and launching too many instances before the first one even finishes booting.

**CloudWatch Alarms**
CloudWatch is AWS's monitoring and observability service. It tracks metrics published by AWS services (like `CPUUtilization` for EC2).
- **Namespaces and Dimensions:** You specified namespace `AWS/EC2` and Dimension `AutoScalingGroupName`. This tells CloudWatch to look at the aggregated CPU usage of all instances within your specific ASG, rather than just a single instance.
- **Scale Up Alarm:** Triggers when Average CPU is `>= 20.0%` for 2 consecutive evaluation periods of 60 seconds (total 2 minutes). When triggered, its `AlarmActions` executes the Scale Out Policy ARN.
- **Scale Down Alarm:** Triggers when Average CPU is `<= 30.0%` for 2 consecutive periods. When triggered, it executes the Scale In Policy.
*(Note: Usually, scale-down thresholds are much lower than scale-up (e.g., scale up at 80%, scale down at 30%) to prevent "flapping"—the rapid scaling in and out of instances. However, 20% and 30% were configured as per lab requirements).*

---

## Topic 5: Stress Testing and Triggering Scaling

To prove the auto-scaling works, you need to simulate traffic to force the CPU utilization up. You have two scripts for this:

1. **`stress_test.py` (Local Execution):** Uses Python `threading` and `urllib` to rapidly hit the web server's URL. The threads send concurrent HTTP requests, forcing the EC2 instance's CPU to work hard to process the requests and serve the Apache index page.
2. **`load_generator.py` (Cloud Execution):** Instead of using your local machine, this launches a temporary EC2 instance in AWS. Its UserData installs `apache2-utils` and runs `ab` (Apache Benchmark) in a loop (`ab -n 500000 -c 200`). 
   - *Why is this better?* Network latency from your laptop to AWS slows down the rate of requests. An EC2 instance running in the same AWS data center has practically zero latency and immense bandwidth, making it capable of instantly maxing out a small `t3.micro` instance's CPU.

**The Viva Walkthrough of a Scaling Event:**
1. You run the load generator against your ASG's current instance.
2. The `t3.micro` instance CPU spikes past 20%.
3. CloudWatch records this metric. After 2 minutes, the metric remains above 20%.
4. The CloudWatch Alarm state changes from `OK` to `ALARM`.
5. The Alarm triggers the ASG Scale Out Policy ARN.
6. The ASG provisions a new instance using the configured Launch Template.
7. You refresh the browser and eventually see a different `Instance ID` on the webpage (if you hit the new instance).
8. Once the load generator script finishes or is terminated, the CPU drops below 30% for 2 minutes.
9. This triggers the Scale Down alarm, and the ASG terminates the extra instance to save money, returning to `DesiredCapacity` of 1.

---

## Likely Viva Questions to Prepare For:

1. **"What happens if an instance is manually deleted from the AWS Console or crashes?"** 
   *Answer:* The ASG constantly performs health checks. It detects that the healthy instance count has dropped below `MinSize` (or `DesiredCapacity`), and it will automatically launch a new instance to replace it. This is called self-healing.

2. **"Why use Base64 encoding for the UserData?"**
   *Answer:* The AWS API expects UserData to be a base64 encoded string when passed into Launch Templates (and some specific boto3 functions) to ensure special characters, binary files (like our tarball), and formatting are preserved safely during transit over HTTP to the AWS API.

3. **"How does the newly scaled instance get the website files?"**
   *Answer:* Because the ASG uses the Launch Template, and the Launch Template contains the `startup.sh` UserData script. Every new instance runs that exact script on boot, creating the tarball, unzipping the website files, and modifying the HTML to show its own unique Instance ID automatically.

4. **"What is the difference between ScaleOut and ScaleIn policies?"**
   *Answer:* ScaleOut increases capacity (Adjustment = +1) when load is high to maintain performance. ScaleIn decreases capacity (Adjustment = -1) when load is low to save costs.

5. **"Why did you use IMDSv2 instead of just fetching the metadata URL directly?"**
   *Answer:* Fetching the token first and passing it in a header is the IMDSv2 way. It provides defense-in-depth against SSRF (Server-Side Request Forgery) attacks, whereas IMDSv1 allowed direct retrieval which could be exploited if a vulnerability existed in the web application.

6. **"What does `TreatMissingData='missing'` mean in the CloudWatch alarm?"**
   *Answer:* It tells CloudWatch how to handle situations where it stops receiving data points from EC2 (e.g., if the instance shuts down or loses networking). By setting it to 'missing', CloudWatch doesn't automatically assume the alarm should trigger or recover; it simply evaluates the state based on the actual data it has until new data arrives.
