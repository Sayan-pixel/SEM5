#!/bin/bash

# Update package lists
sudo apt-get update -y

# Install Apache2 HTTP server
sudo apt-get install -y apache2

# Start and enable Apache service
sudo systemctl start apache2
sudo systemctl enable apache2

# Fetch EC2 Instance ID (IMDSv2 with IMDSv1 fallback)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
else
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
fi

# Fallback if metadata service is unavailable
if [ -z "$INSTANCE_ID" ]; then
    INSTANCE_ID="Local-EC2-Instance"
fi

# Remove default Apache index page
sudo rm -rf /var/www/html/*

# Deploy website files to Apache root
cat << 'EOF' > /tmp/website.tar.gz.b64
WEBSITE_TAR_B64_PLACEHOLDER
EOF
base64 -di /tmp/website.tar.gz.b64 > /tmp/website.tar.gz
sudo tar -xzf /tmp/website.tar.gz -C /var/www/html/

# Inject Instance ID into index.html
if [ -f "/var/www/html/index.html" ]; then
    sudo sed -i "s/Fetching.../${INSTANCE_ID}/g" /var/www/html/index.html
fi

# Ensure proper permissions for web server
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
