# AWS Infrastructure Projects

A comprehensive collection of AWS infrastructure projects providing enterprise-grade solutions for multi-VPC environments, landing zones, and infrastructure auditing. Each project is designed to be independent, well-documented, and production-ready.

## 📁 Project Structure

```
desktop-tutorial/
├── README.md                           # This documentation
├── projects/                           # Main projects directory
│   ├── multi-vpc-aws/                 # Multi-VPC AWS Environment
│   ├── aws-landing-zone/              # AWS Landing Zone with Automation
│   └── aws-audit-framework/           # AWS Infrastructure Audit Framework
├── CLOUDFORMATION_COMPARISON.md        # Comparison documentation
└── .gitignore                         # Git ignore file
```

## 🚀 Quick Start

### 1. Multi-VPC AWS Environment
```bash
cd projects/multi-vpc-aws
# See README.md for detailed instructions
```

### 2. AWS Landing Zone
```bash
cd projects/aws-landing-zone
# See README.md for detailed instructions
```

### 3. AWS Audit Framework
```bash
cd projects/aws-audit-framework
# See README.md for detailed instructions
```

## 📋 Project Overview

### 🏗️ Multi-VPC AWS Environment
**Location:** `projects/multi-vpc-aws/`

A comprehensive multi-VPC AWS infrastructure solution with production-ready networking, security, and compute resources. Provides both Terraform and CloudFormation implementations.

**Key Features:**
- ✅ Four VPCs (Production, Development, DMZ, Shared Services)
- ✅ Multi-AZ deployment with high availability
- ✅ VPC peering for inter-VPC communication
- ✅ Auto scaling groups and load balancers
- ✅ RDS database instances with encryption
- ✅ Comprehensive security groups and NACLs
- ✅ CloudWatch monitoring and alerting

**Technologies:**
- Terraform (Infrastructure as Code)
- AWS CloudFormation (JSON templates)
- AWS VPC, EC2, RDS, Auto Scaling
- CloudWatch, SNS, IAM

### 🏢 AWS Landing Zone with Automation
**Location:** `projects/aws-landing-zone/`

A comprehensive AWS Landing Zone implementation with automated setup, governance, and security controls for enterprise environments. Three deployment options available.

**Key Features:**
- ✅ AWS Control Tower automation
- ✅ Terraform implementation with full configuration
- ✅ CloudFormation implementation with deployment scripts
- ✅ Account provisioning automation
- ✅ AWS Organizations and SSO setup
- ✅ Service Control Policies (SCPs)
- ✅ Centralized logging and monitoring

**Technologies:**
- AWS Control Tower
- Terraform (Infrastructure as Code)
- AWS CloudFormation (JSON templates)
- AWS Organizations, SSO, Config
- CloudTrail, CloudWatch, SNS

### 🔍 AWS Infrastructure Audit Framework
**Location:** `projects/aws-audit-framework/`

A comprehensive AWS infrastructure audit solution that provides security, compliance, cost, and performance auditing using both Python (boto3) and Terraform implementations.

**Key Features:**
- ✅ Security audits (IAM, Security Groups, VPC, Encryption)
- ✅ Cost audits (utilization, optimization, budget analysis)
- ✅ Performance audits (CloudWatch metrics, bottlenecks)
- ✅ Compliance audits (Config rules, CIS benchmarks)
- ✅ Infrastructure audits (inventory, drift, best practices)
- ✅ Automated report generation (HTML, PDF, JSON, CSV)
- ✅ CI/CD integration and scheduled audits

**Technologies:**
- Python (boto3) for audit automation
- Terraform for audit infrastructure
- AWS Config, CloudWatch, CloudTrail
- AWS Cost Explorer, Security Hub, GuardDuty

## 🛠️ Technology Stack

### Infrastructure as Code
- **Terraform** - HashiCorp's infrastructure automation tool
- **AWS CloudFormation** - AWS-native infrastructure templates
- **Python (boto3)** - AWS SDK for Python automation

### AWS Services
- **Compute:** EC2, Auto Scaling, Lambda
- **Networking:** VPC, Route Tables, Security Groups, NACLs
- **Database:** RDS, DynamoDB
- **Storage:** S3, EBS
- **Security:** IAM, KMS, GuardDuty, Security Hub
- **Monitoring:** CloudWatch, CloudTrail, Config
- **Management:** Organizations, SSO, Control Tower

### Development Tools
- **Git** - Version control
- **Shell Scripts** - Automation and deployment
- **YAML/JSON** - Configuration files
- **Markdown** - Documentation

## 🔧 Prerequisites

### General Requirements
- **AWS CLI** installed and configured
- **Git** for version control
- **jq** for JSON processing (optional but recommended)

### Project-Specific Requirements

#### Multi-VPC AWS Environment
- **Terraform** (for Terraform implementation)
- **AWS Account** with appropriate permissions

#### AWS Landing Zone
- **Python 3.8+** (for automation scripts)
- **AWS Account** with Organizations access
- **Terraform** (for Terraform implementation)

#### AWS Audit Framework
- **Python 3.8+** (for Python implementation)
- **Terraform** (for Terraform implementation)
- **AWS Account** with audit permissions

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/uklm97/desktop-tutorial.git
cd desktop-tutorial
```

### 2. Choose Your Project
Navigate to the project you want to deploy:

```bash
# For Multi-VPC Environment
cd projects/multi-vpc-aws

# For Landing Zone
cd projects/aws-landing-zone

# For Audit Framework
cd projects/aws-audit-framework
```

### 3. Follow Project-Specific Instructions
Each project has its own comprehensive README with:
- Detailed architecture documentation
- Step-by-step deployment instructions
- Configuration options
- Troubleshooting guides
- Best practices

## 📊 Project Comparison

| Feature | Multi-VPC AWS | Landing Zone | Audit Framework |
|---------|---------------|--------------|-----------------|
| **Purpose** | Infrastructure deployment | Account governance | Infrastructure auditing |
| **Scope** | Multi-VPC networking | Multi-account setup | Security & compliance |
| **Terraform** | ✅ Full implementation | ✅ Custom implementation | ✅ Infrastructure setup |
| **CloudFormation** | ✅ JSON templates | ✅ JSON templates | ❌ Not applicable |
| **Python** | ❌ Not applicable | ✅ Automation scripts | ✅ Core audit engine |
| **AWS Control Tower** | ❌ Not applicable | ✅ Full integration | ❌ Not applicable |
| **Multi-Account** | ❌ Single account | ✅ Multi-account | ✅ Cross-account |
| **Security Focus** | Network security | Governance & compliance | Security auditing |
| **Cost Management** | Basic monitoring | Budget controls | Cost optimization |

## 🔒 Security Features

### Multi-VPC AWS Environment
- **Network Segmentation** - Proper subnet isolation
- **Security Groups** - Instance-level firewall rules
- **Network ACLs** - Subnet-level access control
- **VPC Flow Logs** - Network traffic monitoring
- **Encryption** - Data encryption at rest and in transit

### AWS Landing Zone
- **Service Control Policies** - Account-level restrictions
- **AWS SSO** - Centralized identity management
- **Guardrails** - Automated compliance controls
- **Centralized Logging** - All logs in dedicated account
- **MFA Enforcement** - Multi-factor authentication

### AWS Audit Framework
- **Security Audits** - IAM, security groups, encryption
- **Compliance Monitoring** - Config rules, CIS benchmarks
- **Cost Analysis** - Resource utilization, optimization
- **Performance Monitoring** - CloudWatch metrics, bottlenecks
- **Automated Reporting** - Multiple format outputs

## 💰 Cost Optimization

### Multi-VPC AWS Environment
- **Auto Scaling** - Scale based on demand
- **Reserved Instances** - Long-term cost savings
- **Spot Instances** - Cost-effective compute resources
- **S3 Lifecycle** - Automated storage optimization

### AWS Landing Zone
- **Budget Alerts** - Cost threshold notifications
- **Resource Tagging** - Cost allocation tracking
- **Account Limits** - Prevent cost overruns
- **Optimization Recommendations** - Automated suggestions

### AWS Audit Framework
- **Cost Audits** - Resource utilization analysis
- **Optimization Reports** - Cost savings recommendations
- **Unused Resource Detection** - Cleanup opportunities
- **Budget Monitoring** - Cost trend analysis

## 🔄 Automation and CI/CD

### Multi-VPC AWS Environment
- **Terraform Automation** - Infrastructure as Code
- **CloudFormation Stacks** - Automated deployment
- **Shell Scripts** - Deployment automation

### AWS Landing Zone
- **Account Provisioning** - Automated account creation
- **Control Tower Setup** - Automated landing zone deployment
- **Policy Application** - Automated SCP deployment

### AWS Audit Framework
- **Scheduled Audits** - Automated compliance checks
- **CI/CD Integration** - GitHub Actions workflows
- **Report Generation** - Automated documentation
- **Alert Notifications** - Automated security alerts

## 📈 Monitoring and Observability

### Multi-VPC AWS Environment
- **CloudWatch Dashboards** - Infrastructure monitoring
- **VPC Flow Logs** - Network traffic analysis
- **Auto Scaling Alarms** - Performance monitoring
- **RDS Monitoring** - Database performance

### AWS Landing Zone
- **Centralized Logging** - All accounts to log archive
- **Security Hub** - Security findings aggregation
- **Config Compliance** - Resource configuration monitoring
- **CloudTrail** - API call logging

### AWS Audit Framework
- **Comprehensive Auditing** - Security, cost, performance
- **Automated Reports** - Multiple format outputs
- **Compliance Scoring** - Automated compliance assessment
- **Trend Analysis** - Historical audit data

## 🚨 Troubleshooting

### Common Issues

#### 1. AWS Credentials
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure AWS CLI
aws configure
```

#### 2. Terraform Issues
```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan
```

#### 3. Python Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Check Python version
python3 --version
```

### Project-Specific Troubleshooting
Each project includes detailed troubleshooting guides in their respective README files.

## 📞 Support and Resources

### Documentation
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Python boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Community Resources
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Registry](https://registry.terraform.io/)

### Professional Services
- AWS Professional Services
- AWS Partner Network
- AWS Managed Services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Contribution Guidelines
- Follow the existing code style and structure
- Update documentation for any changes
- Test your changes thoroughly
- Ensure security best practices are followed

## 📄 License

This project is provided as-is for educational and demonstration purposes. Please review and modify according to your specific requirements and security policies.

## 📝 Changelog

### Version 2.0.0 - Project Restructuring
- **Restructured** all projects into separate, well-organized directories
- **Enhanced** documentation for each project
- **Improved** project structure and organization
- **Added** comprehensive README files for each project
- **Updated** all paths and references

### Version 1.0.0 - Initial Release
- **Multi-VPC AWS Environment** - Complete infrastructure solution
- **AWS Landing Zone** - Enterprise governance and automation
- **AWS Audit Framework** - Comprehensive infrastructure auditing
- **Terraform and CloudFormation** implementations
- **Python automation** scripts and tools

## 🔗 Related Projects

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Landing Zone](https://aws.amazon.com/solutions/implementations/aws-landing-zone/)
- [AWS Control Tower](https://aws.amazon.com/controltower/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

**Note:** This repository contains multiple independent AWS infrastructure projects. Each project can be used separately or in combination depending on your specific requirements. Please refer to individual project README files for detailed instructions and documentation.
