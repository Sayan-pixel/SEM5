# Name: Sayan Shit
# Roll No: 2401179

import boto3
import base64
import time

def main():
    ec2 = boto3.client('ec2', region_name='ap-south-1')
    autoscaling = boto3.client('autoscaling', region_name='ap-south-1')
    cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
    
    # 1. Fetch startup script
    with open('startup.sh', 'r') as f:
        user_data_script = f.read()
        
    with open('base64.txt', 'r') as f:
        tar_b64 = f.read().replace('\r', '').strip()
        
    user_data_script = user_data_script.replace('WEBSITE_TAR_B64_PLACEHOLDER', tar_b64)
    encoded_user_data = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')
    
    # 2. Get Security Group (reusing the one from a5_q2.py)
    try:
        sg_info = ec2.describe_security_groups(GroupNames=['portfolio-web-sg'])
        security_group_id = sg_info['SecurityGroups'][0]['GroupId']
    except Exception as e:
        print(f"Error fetching Security Group (Did you run a5_q2.py first?): {e}")
        return
        
    ami_id = 'ami-03f4878755434977f' # Ubuntu 22.04 LTS ap-south-1
    template_name = 'Lab5-Portfolio-LT'
    asg_name = 'Lab5-Portfolio-ASG'
    
    # 3. Create Launch Template
    print(f"Creating Launch Template: {template_name}...")
    try:
        ec2.create_launch_template(
            LaunchTemplateName=template_name,
            LaunchTemplateData={
                'ImageId': ami_id,
                'InstanceType': 't3.micro',
                'SecurityGroupIds': [security_group_id],
                'UserData': encoded_user_data
            }
        )
        print("Launch Template created successfully.")
    except ec2.exceptions.ClientError as e:
        if 'InvalidLaunchTemplateName.AlreadyExistsException' in str(e):
            print(f"Launch Template {template_name} already exists. Proceeding...")
        else:
            print(f"Error creating launch template: {e}")
            return

    # 4. Create Auto Scaling Group (ASG)
    print(f"Creating Auto Scaling Group: {asg_name}...")
    try:
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                'LaunchTemplateName': template_name,
                'Version': '$Latest'
            },
            MinSize=1,
            MaxSize=3,
            DesiredCapacity=1,
            AvailabilityZones=['ap-south-1a', 'ap-south-1b']
        )
        print("Auto Scaling Group created successfully.")
    except autoscaling.exceptions.AlreadyExistsFault:
        print(f"ASG {asg_name} already exists. Proceeding...")
    except Exception as e:
        print(f"Error creating ASG: {e}")
        return
        
    # Wait for ASG to be ready
    time.sleep(5)
    
    # 5. Create Scaling Policies
    print("Creating Scaling Policies...")
    scale_out_response = autoscaling.put_scaling_policy(
        AutoScalingGroupName=asg_name,
        PolicyName='ScaleOutPolicy',
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=1,
        Cooldown=60
    )
    scale_out_arn = scale_out_response['PolicyARN']
    
    scale_in_response = autoscaling.put_scaling_policy(
        AutoScalingGroupName=asg_name,
        PolicyName='ScaleInPolicy',
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=-1,
        Cooldown=60
    )
    scale_in_arn = scale_in_response['PolicyARN']
    print("Scaling Policies created successfully.")
    
    # 6. Create CloudWatch Alarms
    print("Creating CloudWatch Alarms...")
    cloudwatch.put_metric_alarm(
        AlarmName='Lab5-ScaleUp-Alarm',
        AlarmDescription='Alarm to scale up ASG when CPU > 20%',
        ActionsEnabled=True,
        AlarmActions=[scale_out_arn],
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistic='Average',
        Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
        Period=60,
        EvaluationPeriods=2,
        Threshold=20.0,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        TreatMissingData='missing'
    )
    
    cloudwatch.put_metric_alarm(
        AlarmName='Lab5-ScaleDown-Alarm',
        AlarmDescription='Alarm to scale down ASG when CPU <= 30%',
        ActionsEnabled=True,
        AlarmActions=[scale_in_arn],
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistic='Average',
        Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
        Period=60,
        EvaluationPeriods=2,
        Threshold=30.0,
        ComparisonOperator='LessThanOrEqualToThreshold',
        TreatMissingData='missing'
    )
    print("CloudWatch Alarms created successfully.")
    print("\n--- Auto Scaling Infrastructure Deployed! ---")
    print("Please head to the AWS Console to verify the ASG and CloudWatch Alarms.")

if __name__ == "__main__":
    main()
