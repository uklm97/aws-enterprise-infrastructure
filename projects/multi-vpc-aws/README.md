# Multi-VPC AWS Environment

A comprehensive multi-VPC AWS infrastructure solution with production-ready networking, security, and compute resources. This project provides both Terraform and CloudFormation implementations for creating a secure, scalable AWS environment.

## 🏗️ Architecture Overview

### VPC Structure
```
AWS Multi-VPC Environment
├── Production VPC (10.0.0.0/16)
│   ├── Public Subnets (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)
│   ├── Private Subnets (10.0.11.0/24, 10.0.12.0/24, 10.0.13.0/24)
│   └── Database Subnets (10.0.21.0/24, 10.0.22.0/24, 10.0.23.0/24)
├── Development VPC (10.1.0.0/16)
│   ├── Public Subnets (10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24)
│   ├── Private Subnets (10.1.11.0/24, 10.1.12.0/24, 10.1.13.0/24)
│   └── Database Subnets (10.1.21.0/24, 10.1.22.0/24, 10.1.23.0/24)
├── DMZ VPC (10.2.0.0/16)
│   ├── Public Subnets (10.2.1.0/24, 10.2.2.0/24, 10.2.3.0/24)
│   └── Private Subnets (10.2.11.0/24, 10.2.12.0/24, 10.2.13.0/24)
└── Shared Services VPC (10.3.0.0/16)
    ├── Public Subnets (10.3.1.0/24, 10.3.2.0/24, 10.3.3.0/24)
    ├── Private Subnets (10.3.11.0/24, 10.3.12.0/24, 10.3.13.0/24)
    └── Database Subnets (10.3.21.0/24, 10.3.22.0/24, 10.3.23.0/24)
```

### Network Components
- **Internet Gateways** - Public internet access
- **NAT Gateways** - Private subnet internet access
- **VPC Peering** - Inter-VPC communication
- **Route Tables** - Traffic routing control
- **Security Groups** - Instance-level security
- **Network ACLs** - Subnet-level security

## 📁 Project Structure

```
multi-vpc-aws/
├── README.md                           # This documentation
├── ARCHITECTURE.md                     # Detailed architecture documentation
├── main.tf                            # Main Terraform configuration
├── variables.tf                       # Terraform variables
├── vpcs.tf                           # VPC and networking resources
├── security.tf                       # Security groups and NACLs
├── vpc-peering.tf                    # VPC peering configuration
├── compute.tf                        # EC2 instances and load balancers
├── database.tf                       # RDS database instances
├── outputs.tf                        # Terraform outputs
├── user_data.sh                      # EC2 user data script
├── bastion_user_data.sh              # Bastion host user data
├── terraform.tfvars.example          # Example variables file
├── ssh_key                           # SSH private key
├── ssh_key.pub                       # SSH public key
├── .gitignore                        # Git ignore file
└── cloudformation/                   # CloudFormation implementation
    ├── main.json                     # Main CloudFormation template
    ├── networking.json               # Networking resources
    ├── security.json                 # Security resources
    ├── deploy.sh                     # Deployment script
    └── README.md                     # CloudFormation documentation
```

## 🚀 Quick Start

### Prerequisites
1. **AWS CLI** installed and configured
2. **Terraform** (for Terraform implementation)
3. **jq** (for JSON processing in scripts)

### Terraform Implementation

#### 1. Initialize Terraform
```bash
cd projects/multi-vpc-aws
terraform init
```

#### 2. Configure Variables
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

#### 3. Plan and Apply
```bash
terraform plan
terraform apply
```

### CloudFormation Implementation

#### 1. Deploy Infrastructure
```bash
cd projects/multi-vpc-aws/cloudformation
./deploy.sh
```

#### 2. Validate Deployment
```bash
./deploy.sh -v
```

## 🔧 Core Features

### 1. Multi-VPC Architecture
- **Production VPC** - High-availability production workloads
- **Development VPC** - Development and testing environments
- **DMZ VPC** - Public-facing services and load balancers
- **Shared Services VPC** - Common services and databases

### 2. Networking
- **Multi-AZ Deployment** - High availability across availability zones
- **Public/Private Subnets** - Proper network segmentation
- **Database Subnets** - Isolated database environments
- **VPC Peering** - Secure inter-VPC communication
- **Internet Connectivity** - Controlled internet access

### 3. Security
- **Security Groups** - Instance-level firewall rules
- **Network ACLs** - Subnet-level access control
- **Bastion Host** - Secure SSH access to private instances
- **Encryption** - Data encryption at rest and in transit
- **IAM Roles** - Least privilege access control

### 4. Compute Resources
- **Auto Scaling Groups** - Automatic scaling based on demand
- **Application Load Balancers** - Traffic distribution
- **EC2 Instances** - Web servers and application instances
- **Launch Templates** - Standardized instance configurations

### 5. Database
- **RDS MySQL Instances** - Managed database services
- **Multi-AZ Deployment** - Database high availability
- **Automated Backups** - Point-in-time recovery
- **Performance Monitoring** - CloudWatch integration

### 6. Monitoring and Logging
- **CloudWatch Alarms** - Performance and availability monitoring
- **VPC Flow Logs** - Network traffic logging
- **Auto Scaling Policies** - Automated scaling based on metrics
- **Health Checks** - Application and database health monitoring

## 🛠️ Configuration Options

### Environment Variables
```bash
# AWS Region
export AWS_REGION=us-east-1

# Project Configuration
export PROJECT_NAME=my-multi-vpc
export ENVIRONMENT=production
```

### Terraform Variables
```hcl
# VPC Configuration
vpc_cidr_blocks = {
  production     = "10.0.0.0/16"
  development    = "10.1.0.0/16"
  dmz           = "10.2.0.0/16"
  shared_services = "10.3.0.0/16"
}

# Instance Configuration
instance_type = "t3.micro"
ami_id        = "ami-12345678"

# Database Configuration
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
```

### CloudFormation Parameters
```json
{
  "Parameters": {
    "Environment": {
      "Type": "String",
      "Default": "production"
    },
    "ProjectName": {
      "Type": "String",
      "Default": "multi-vpc-aws"
    }
  }
}
```

## 🔄 Deployment Workflows

### Terraform Workflow
```bash
# 1. Initialize
terraform init

# 2. Plan changes
terraform plan -var-file="terraform.tfvars"

# 3. Apply changes
terraform apply -var-file="terraform.tfvars"

# 4. Destroy (if needed)
terraform destroy -var-file="terraform.tfvars"
```

### CloudFormation Workflow
```bash
# 1. Validate templates
./deploy.sh -v

# 2. Deploy infrastructure
./deploy.sh -c

# 3. Update infrastructure
./deploy.sh -u

# 4. Delete infrastructure
./deploy.sh -d
```

## 📊 Monitoring and Alerts

### CloudWatch Dashboards
- **VPC Dashboard** - Network performance and utilization
- **Application Dashboard** - Application performance metrics
- **Database Dashboard** - Database performance and health
- **Security Dashboard** - Security events and compliance

### Alerts and Notifications
- **High CPU Usage** - Instance performance alerts
- **Database Connections** - Database performance alerts
- **Auto Scaling Events** - Scaling activity notifications
- **Security Events** - Security group and NACL changes

## 🔒 Security Best Practices

### Network Security
- **Network Segmentation** - Proper subnet isolation
- **Security Groups** - Restrictive inbound/outbound rules
- **Network ACLs** - Additional subnet-level protection
- **VPC Flow Logs** - Network traffic monitoring

### Access Control
- **Bastion Host** - Controlled SSH access
- **IAM Roles** - Instance-level permissions
- **SSH Key Management** - Secure key distribution
- **Least Privilege** - Minimal required permissions

### Data Protection
- **Encryption at Rest** - EBS and RDS encryption
- **Encryption in Transit** - TLS/SSL for all communications
- **Backup Encryption** - Automated backup protection
- **Key Management** - AWS KMS integration

## 💰 Cost Optimization

### Resource Optimization
- **Auto Scaling** - Scale based on demand
- **Spot Instances** - Cost-effective compute resources
- **Reserved Instances** - Long-term cost savings
- **S3 Lifecycle** - Automated storage optimization

### Monitoring and Alerts
- **Cost Alerts** - Budget threshold notifications
- **Resource Utilization** - Performance monitoring
- **Unused Resources** - Cleanup recommendations
- **Cost Allocation** - Tag-based cost tracking

## 🚨 Troubleshooting

### Common Issues

#### 1. VPC Peering Issues
```bash
# Check VPC peering status
aws ec2 describe-vpc-peering-connections

# Verify route table entries
aws ec2 describe-route-tables
```

#### 2. Security Group Issues
```bash
# Check security group rules
aws ec2 describe-security-groups

# Test connectivity
aws ec2 describe-network-interfaces
```

#### 3. Auto Scaling Issues
```bash
# Check Auto Scaling groups
aws autoscaling describe-auto-scaling-groups

# View scaling activities
aws autoscaling describe-scaling-activities
```

### Debugging Commands
```bash
# Check VPC status
aws ec2 describe-vpcs

# Verify subnet configuration
aws ec2 describe-subnets

# Check route tables
aws ec2 describe-route-tables

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics
```

## 📈 Scaling and Extensions

### Horizontal Scaling
- **Auto Scaling Groups** - Automatic instance scaling
- **Load Balancers** - Traffic distribution
- **Multi-AZ Deployment** - High availability
- **Database Read Replicas** - Database scaling

### Vertical Scaling
- **Instance Type Changes** - Upgrade instance types
- **Database Instance Class** - Upgrade database performance
- **Storage Scaling** - Increase storage capacity
- **Memory Optimization** - Optimize memory usage

### Third-Party Integrations
- **Monitoring Tools** - DataDog, New Relic, etc.
- **Logging Services** - Splunk, ELK Stack, etc.
- **Security Tools** - GuardDuty, Security Hub, etc.
- **CI/CD Tools** - Jenkins, GitLab CI, etc.

## 📞 Support and Resources

### Documentation
- [AWS VPC User Guide](https://docs.aws.amazon.com/vpc/)
- [AWS Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/)
- [AWS RDS User Guide](https://docs.aws.amazon.com/rds/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

### Community Resources
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Registry](https://registry.terraform.io/)

### Professional Services
- AWS Professional Services
- AWS Partner Network
- AWS Managed Services

## 📄 License

This project is provided as-is for educational and demonstration purposes. Please review and modify according to your specific requirements and security policies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 Changelog

### Version 1.0.0
- Initial release with Terraform and CloudFormation implementations
- Multi-VPC architecture with four VPCs
- Complete networking, security, and compute resources
- Auto scaling and load balancing capabilities
- RDS database instances with high availability
- Comprehensive monitoring and alerting
