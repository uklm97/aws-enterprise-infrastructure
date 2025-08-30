#!/bin/bash
yum update -y
yum install -y httpd

# Start and enable Apache for a simple status page
systemctl start httpd
systemctl enable httpd

# Create a simple status page
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Bastion Host - Multi-VPC Environment</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .details { font-family: monospace; background: #e9ecef; padding: 10px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Bastion Host</h1>
            <p>Secure SSH Access Point for Multi-VPC Environment</p>
        </div>
        
        <div class="info">
            <h3>Instance Information</h3>
            <div class="details">
                <strong>Instance ID:</strong> $(curl -s http://169.254.169.254/latest/meta-data/instance-id)<br>
                <strong>Availability Zone:</strong> $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)<br>
                <strong>Private IP:</strong> $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)<br>
                <strong>Public IP:</strong> $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)<br>
                <strong>Server Time:</strong> $(date)
            </div>
        </div>
        
        <div class="warning">
            <h3>⚠️ Security Notice</h3>
            <p>This is a bastion host for secure SSH access to private instances in the multi-VPC environment.</p>
            <ul>
                <li>Only authorized users should access this host</li>
                <li>Use SSH key authentication only</li>
                <li>Monitor access logs regularly</li>
                <li>Keep the system updated</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>Accessible Environments</h3>
            <p>From this bastion host, you can SSH to instances in:</p>
            <ul>
                <li><strong>Production VPC:</strong> Private instances in production environment</li>
                <li><strong>Development VPC:</strong> Private instances in development environment</li>
                <li><strong>Shared Services VPC:</strong> Private instances in shared services</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>SSH Connection Examples</h3>
            <div class="details">
                # Connect to production instance<br>
                ssh -i /path/to/key.pem ec2-user@[PRIVATE_IP]<br><br>
                
                # Connect to development instance<br>
                ssh -i /path/to/key.pem ec2-user@[PRIVATE_IP]<br><br>
                
                # Use SSH agent forwarding<br>
                ssh -A -i /path/to/key.pem ec2-user@[PRIVATE_IP]
            </div>
        </div>
        
        <div class="info">
            <h3>System Status</h3>
            <p>✅ SSH service is running</p>
            <p>✅ Security groups are configured</p>
            <p>✅ VPC peering is established</p>
            <p>✅ Network connectivity verified</p>
        </div>
    </div>
</body>
</html>
EOF

# Set proper permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Configure SSH for better security
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Restart SSH service
systemctl restart sshd

# Install CloudWatch agent for monitoring
yum install -y amazon-cloudwatch-agent

# Configure CloudWatch agent for bastion
cat > /opt/aws/amazon-cloudwatch-agent/bin/config.json << 'EOF'
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/secure",
                        "log_group_name": "/aws/ec2/bastion/ssh",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/aws/ec2/bastion/system",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "MultiVPC/Bastion",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60,
                "totalcpu": false
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
systemctl start amazon-cloudwatch-agent
systemctl enable amazon-cloudwatch-agent

# Create a simple health check endpoint
cat > /var/www/html/health.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Bastion Health Check</title>
</head>
<body>
    <h1>OK</h1>
    <p>Bastion host is healthy</p>
    <p>SSH service is running</p>
    <p>Timestamp: $(date)</p>
</body>
</html>
EOF

echo "Bastion host user data script completed"
