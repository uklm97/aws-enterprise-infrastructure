#!/bin/bash
yum update -y
yum install -y httpd php php-mysqlnd

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Create a simple PHP application
cat > /var/www/html/index.php << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Multi-VPC Demo - ${environment}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .status { color: #28a745; font-weight: bold; }
        .details { font-family: monospace; background: #e9ecef; padding: 10px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Multi-VPC AWS Environment</h1>
            <p>Environment: <span class="status">${environment}</span></p>
        </div>
        
        <div class="info">
            <h3>Instance Information</h3>
            <div class="details">
                <strong>Instance ID:</strong> <?php echo $_SERVER['HTTP_X_AWS_EC2_INSTANCE_ID'] ?? 'N/A'; ?><br>
                <strong>Availability Zone:</strong> <?php echo $_SERVER['HTTP_X_AWS_EC2_AVAILABILITY_ZONE'] ?? 'N/A'; ?><br>
                <strong>Private IP:</strong> <?php echo $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'N/A'; ?><br>
                <strong>Server Time:</strong> <?php echo date('Y-m-d H:i:s T'); ?>
            </div>
        </div>
        
        <div class="info">
            <h3>Environment Details</h3>
            <p>This is the <strong>${environment}</strong> environment running in a multi-VPC AWS setup.</p>
            <ul>
                <li>✅ Load Balancer: Application Load Balancer</li>
                <li>✅ Auto Scaling: Configured for high availability</li>
                <li>✅ Security Groups: Properly configured</li>
                <li>✅ VPC Peering: Connected to other environments</li>
                <li>✅ Database: RDS MySQL instance</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>Architecture Overview</h3>
            <p>This multi-VPC environment includes:</p>
            <ul>
                <li><strong>Production VPC:</strong> High-availability production workloads</li>
                <li><strong>Development VPC:</strong> Development and testing environment</li>
                <li><strong>DMZ VPC:</strong> Public-facing services and bastion host</li>
                <li><strong>Shared Services VPC:</strong> Common databases and monitoring</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>Health Check</h3>
            <p>✅ Web server is running and responding</p>
            <p>✅ PHP is working correctly</p>
            <p>✅ Load balancer health checks should pass</p>
        </div>
    </div>
</body>
</html>
EOF

# Set proper permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Create a health check endpoint
cat > /var/www/html/health.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Health Check</title>
</head>
<body>
    <h1>OK</h1>
    <p>Server is healthy</p>
    <p>Environment: ${environment}</p>
    <p>Timestamp: $(date)</p>
</body>
</html>
EOF

# Install CloudWatch agent for monitoring
yum install -y amazon-cloudwatch-agent

# Configure CloudWatch agent
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
                        "file_path": "/var/log/httpd/access_log",
                        "log_group_name": "/aws/ec2/${environment}/apache/access",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/httpd/error_log",
                        "log_group_name": "/aws/ec2/${environment}/apache/error",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "MultiVPC/${environment}",
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
            "diskio": {
                "measurement": ["io_time"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            },
            "netstat": {
                "measurement": ["tcp_established", "tcp_time_wait"],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": ["swap_used_percent"],
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

echo "User data script completed for ${environment} environment"
