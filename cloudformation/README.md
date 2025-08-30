# Multi-VPC AWS Environment - CloudFormation

This project provides a complete multi-VPC AWS environment using AWS CloudFormation templates in JSON format. The environment includes production, development, DMZ, and shared services VPCs with proper networking, security, and compute resources.

## 🏗️ Architecture Overview

### VPCs
- **Production VPC** (10.0.0.0/16) - High-availability production workloads
- **Development VPC** (10.1.0.0/16) - Development and testing environment
- **DMZ VPC** (10.2.0.0/16) - Public-facing services and bastion host
- **Shared Services VPC** (10.3.0.0/16) - Common databases and monitoring

### Components
- **Networking**: Subnets, route tables, NAT gateways, VPC peering
- **Security**: Security groups, network ACLs, bastion host
- **Compute**: Auto Scaling Groups, Application Load Balancers, EC2 instances
- **Database**: RDS MySQL instances with multi-AZ deployment
- **Monitoring**: CloudWatch alarms and VPC Flow Logs

## 📁 Template Structure

```
cloudformation/
├── main.json              # Main VPCs and Internet Gateways
├── networking.json        # Subnets, Route Tables, NAT Gateways
├── security.json          # Security Groups and Network ACLs
├── compute.json           # EC2, Auto Scaling, Load Balancers
├── database.json          # RDS instances and CloudWatch alarms
├── deploy.sh              # Deployment script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
1. **AWS CLI** installed and configured
2. **AWS Account** with appropriate permissions
3. **SSH Key Pair** for EC2 instances

### Deployment Steps

1. **Clone and navigate to the project:**
   ```bash
   cd cloudformation
   ```

2. **Make the deployment script executable:**
   ```bash
   chmod +x deploy.sh
   ```

3. **Deploy the complete environment:**
   ```bash
   ./deploy.sh deploy
   ```

4. **Or deploy step by step:**
   ```bash
   # Validate templates
   ./deploy.sh validate
   
   # Deploy VPCs
   aws cloudformation create-stack \
     --stack-name multi-vpc-environment-vpc \
     --template-body file://main.json \
     --parameters ParameterKey=Environment,ParameterValue=multi-vpc \
     --capabilities CAPABILITY_IAM
   
   # Deploy networking
   aws cloudformation create-stack \
     --stack-name multi-vpc-environment-networking \
     --template-body file://networking.json \
     --parameters ParameterKey=Environment,ParameterValue=multi-vpc \
     --capabilities CAPABILITY_IAM
   
   # Continue with other stacks...
   ```

## 🔧 Configuration

### Parameters

The templates use the following parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Environment` | `multi-vpc` | Environment name for tagging |
| `ProjectName` | `multi-vpc-demo` | Project name for resource naming |
| `InstanceType` | `t3.micro` | EC2 instance type |
| `DBInstanceClass` | `db.t3.micro` | RDS instance class |
| `DBAllocatedStorage` | `20` | RDS storage in GB |
| `DBEngineVersion` | `8.0.35` | MySQL engine version |
| `EnableNATGateway` | `true` | Enable NAT Gateway for private subnets |
| `EnableVPCFlowLogs` | `true` | Enable VPC Flow Logs |

### Customization

To customize the deployment:

1. **Edit the deployment script:**
   ```bash
   # Modify these variables in deploy.sh
   STACK_NAME="your-stack-name"
   REGION="your-aws-region"
   ENVIRONMENT="your-environment"
   PROJECT_NAME="your-project"
   ```

2. **Use parameter files:**
   ```bash
   # Create a parameters file
   cat > parameters.json << EOF
   [
     {
       "ParameterKey": "Environment",
       "ParameterValue": "production"
     },
     {
       "ParameterKey": "ProjectName",
       "ParameterValue": "my-project"
     }
   ]
   EOF
   
   # Deploy with parameters
   aws cloudformation create-stack \
     --stack-name my-stack \
     --template-body file://main.json \
     --parameters file://parameters.json
   ```

## 🔐 Security Features

### Security Groups
- **Production Web**: HTTP/HTTPS from ALB, SSH from bastion
- **Production ALB**: HTTP/HTTPS from internet
- **Production DB**: MySQL from web servers
- **Development Web**: HTTP/HTTPS from ALB, SSH from bastion
- **Development ALB**: HTTP/HTTPS from internet
- **Development DB**: MySQL from web servers
- **Shared DB**: MySQL from production and development
- **Bastion**: SSH from internet

### Network ACLs
- Allow HTTP (80), HTTPS (443), SSH (22)
- Allow ephemeral ports (1024-65535)
- Applied to all subnets in each VPC

### Access Control
- SSH key authentication only
- Bastion host for secure access
- Private subnets for sensitive resources
- VPC peering for controlled communication

## 📊 Monitoring and Logging

### CloudWatch Alarms
- CPU utilization thresholds for auto scaling
- Database connection monitoring
- Multi-dimensional monitoring

### VPC Flow Logs
- Network traffic monitoring
- Security analysis
- Compliance reporting

### Log Groups
- Application logs
- System logs
- Security logs

## 💰 Cost Optimization

### Development Environment
- Single-AZ RDS deployment
- Smaller instance types
- Reduced backup retention
- Minimal auto scaling

### Production Environment
- Multi-AZ for high availability
- Appropriate instance sizing
- Comprehensive monitoring
- Full backup strategy

## 🛠️ Management Commands

### Deployment Script Usage

```bash
# Deploy complete environment
./deploy.sh deploy

# Validate templates only
./deploy.sh validate

# Display stack outputs
./deploy.sh outputs

# Clean up all stacks
./deploy.sh cleanup
```

### Manual CloudFormation Commands

```bash
# List stacks
aws cloudformation list-stacks --region us-west-2

# Describe stack
aws cloudformation describe-stacks --stack-name multi-vpc-environment-vpc

# Update stack
aws cloudformation update-stack \
  --stack-name multi-vpc-environment-vpc \
  --template-body file://main.json \
  --parameters ParameterKey=Environment,ParameterValue=production

# Delete stack
aws cloudformation delete-stack --stack-name multi-vpc-environment-vpc
```

## 🔄 Stack Dependencies

The stacks must be deployed in the following order:

1. **VPC Stack** (`main.json`) - Creates VPCs and Internet Gateways
2. **Networking Stack** (`networking.json`) - Creates subnets and route tables
3. **Security Stack** (`security.json`) - Creates security groups and NACLs
4. **Compute Stack** (`compute.json`) - Creates EC2, ASG, and ALB
5. **Database Stack** (`database.json`) - Creates RDS instances

## 🚨 Troubleshooting

### Common Issues

1. **Stack Creation Fails**
   - Check AWS CLI configuration
   - Verify template syntax with `./deploy.sh validate`
   - Review CloudFormation events in AWS Console

2. **VPC Peering Issues**
   - Ensure route tables are properly configured
   - Check security group rules
   - Verify CIDR blocks don't overlap

3. **Security Group Errors**
   - Verify security group references
   - Check VPC IDs in imports
   - Ensure proper ingress/egress rules

4. **Database Connection Issues**
   - Verify security group allows MySQL (3306)
   - Check subnet group configuration
   - Ensure database is in private subnets

### Debugging Commands

```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name multi-vpc-environment-vpc

# Validate template
aws cloudformation validate-template \
  --template-body file://main.json

# Check resource status
aws cloudformation describe-stack-resources \
  --stack-name multi-vpc-environment-vpc
```

## 📈 Scaling and Extensions

### Horizontal Scaling
- Auto Scaling Groups automatically scale based on CPU
- Load Balancers distribute traffic across instances
- Multi-AZ deployment for high availability

### Vertical Scaling
- Change instance types in parameters
- Modify RDS instance classes
- Adjust storage allocations

### Additional Services
- **WAF**: Web Application Firewall
- **CloudFront**: Content delivery network
- **ElastiCache**: Redis/Memcached caching
- **S3**: Object storage
- **Lambda**: Serverless functions
- **API Gateway**: REST API management

## 🔒 Security Best Practices

1. **Network Security**
   - Use private subnets for sensitive resources
   - Implement least-privilege security groups
   - Enable VPC Flow Logs for monitoring

2. **Access Control**
   - Use SSH key authentication
   - Implement bastion host access
   - Regular security group reviews

3. **Data Protection**
   - Enable RDS encryption
   - Use HTTPS for web traffic
   - Implement backup strategies

4. **Monitoring**
   - Set up CloudWatch alarms
   - Monitor VPC Flow Logs
   - Regular security audits

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review CloudFormation events in AWS Console
3. Validate templates using the provided script
4. Check AWS CloudFormation documentation

## 📄 License

This project is provided as-is for educational and demonstration purposes. Please review and modify according to your specific requirements and security policies.
