# AWS Landing Zone with Automation

A comprehensive AWS Landing Zone implementation with automated setup, governance, and security controls for enterprise environments. This project provides three deployment options: AWS Control Tower, Terraform, and CloudFormation.

## 🏗️ Architecture Overview

### Core Components
- **Management Account** - Central governance and billing
- **Security Account** - Centralized security and logging
- **Log Archive Account** - Centralized log storage
- **Shared Services Account** - Common services and tools
- **Organizational Units (OUs)** - Logical grouping of accounts
- **Guardrails** - Automated compliance and security controls

### Account Structure
```
AWS Organization
├── Management Account (Root)
│   ├── AWS Control Tower / Terraform / CloudFormation
│   ├── AWS Organizations
│   └── AWS SSO
├── Security OU
│   ├── Security Account
│   └── Log Archive Account
├── Infrastructure OU
│   ├── Shared Services Account
│   └── Network Account
├── Workloads OU
│   ├── Production Accounts
│   ├── Development Accounts
│   └── Testing Accounts
└── Sandbox OU
    └── Sandbox Accounts
```

## 📁 Project Structure

```
aws-landing-zone/
├── README.md                           # This documentation
├── automation/                         # Automation scripts
│   ├── deploy-control-tower.sh        # AWS Control Tower deployment
│   └── create-account.sh              # Account provisioning automation
├── custom/                            # Terraform implementation
│   ├── main.tf                        # Main Terraform configuration
│   └── variables.tf                   # Terraform variables
└── cloudformation/                    # CloudFormation implementation
    ├── main.json                      # Main CloudFormation template
    └── deploy-landing-zone.sh         # CloudFormation deployment script
```

## 🚀 Quick Start

### Prerequisites
1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.8+** for automation scripts
4. **Terraform** (for Terraform implementation)
5. **jq** (for JSON parsing in scripts)

### Deployment Options

#### Option 1: AWS Control Tower (Recommended)
```bash
cd projects/aws-landing-zone/automation
./deploy-control-tower.sh
```

#### Option 2: Terraform Implementation
```bash
cd projects/aws-landing-zone/custom
terraform init
terraform plan
terraform apply
```

#### Option 3: CloudFormation Implementation
```bash
cd projects/aws-landing-zone/cloudformation
./deploy-landing-zone.sh -c
```

## 🛠️ Implementation Options

### Option 1: AWS Control Tower (Recommended)

AWS Control Tower is the recommended approach for most enterprises as it provides:
- **Pre-built best practices** - AWS-managed security and compliance
- **Automated setup** - Quick deployment with minimal configuration
- **Built-in guardrails** - Automated compliance controls
- **Account factory** - Self-service account provisioning

#### Files:
- `automation/deploy-control-tower.sh`

#### Deployment Steps:
```bash
cd projects/aws-landing-zone/automation
./deploy-control-tower.sh
```

#### Features:
- ✅ Automated AWS Organizations setup
- ✅ AWS SSO configuration
- ✅ Built-in guardrails and compliance controls
- ✅ Account Factory for automated account provisioning
- ✅ CloudWatch dashboards and monitoring
- ✅ SNS topics for alerts
- ✅ Budget management and cost optimization

### Option 2: Terraform Implementation

For organizations that prefer Infrastructure as Code with Terraform:

#### Files:
- `custom/main.tf` - Main Terraform configuration
- `custom/variables.tf` - Terraform variables

#### Deployment Steps:
```bash
cd projects/aws-landing-zone/custom

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

#### Features:
- ✅ AWS Organizations with all features enabled
- ✅ Organizational Units (Security, Infrastructure, Workloads, Sandbox)
- ✅ AWS SSO with permission sets (Administrator, Developer, ReadOnly)
- ✅ AWS Config with centralized logging
- ✅ CloudTrail with multi-region support
- ✅ S3 buckets for Config and CloudTrail with encryption
- ✅ CloudWatch dashboards (Executive and Security)
- ✅ SNS topics for alerts
- ✅ Budget alerts and cost management
- ✅ Service Control Policies (SCPs) for security
- ✅ IAM roles and policies
- ✅ Comprehensive tagging strategy

### Option 3: CloudFormation Implementation

For organizations that prefer AWS-native CloudFormation:

#### Files:
- `cloudformation/main.json` - Main CloudFormation template
- `cloudformation/deploy-landing-zone.sh` - Deployment script

#### Deployment Steps:
```bash
cd projects/aws-landing-zone/cloudformation

# Create new landing zone
./deploy-landing-zone.sh -c

# Update existing landing zone
./deploy-landing-zone.sh -u

# Delete landing zone
./deploy-landing-zone.sh -d

# Validate template only
./deploy-landing-zone.sh -v
```

#### Features:
- ✅ AWS Organizations with all features enabled
- ✅ Organizational Units (Security, Infrastructure, Workloads, Sandbox)
- ✅ AWS SSO with permission sets (Administrator, Developer, ReadOnly)
- ✅ AWS Config with centralized logging
- ✅ CloudTrail with multi-region support
- ✅ S3 buckets for Config and CloudTrail with encryption
- ✅ CloudWatch dashboards (Executive and Security)
- ✅ SNS topics for alerts
- ✅ Budget alerts and cost management
- ✅ Service Control Policies (SCPs) for security
- ✅ Conditional resource creation based on parameters
- ✅ Comprehensive outputs and exports

## 🔧 Core Features (All Implementations)

### 1. Account Management
- **Automated Account Provisioning** - Self-service account creation
- **Account Factory** - Standardized account setup
- **Account Vending Machine** - Automated account lifecycle management

### 2. Security & Compliance
- **Guardrails** - Automated compliance controls
- **Security Policies** - Centralized security management
- **Compliance Monitoring** - Real-time compliance reporting
- **Audit Logging** - Comprehensive audit trails

### 3. Identity & Access
- **AWS SSO** - Centralized identity management
- **Permission Sets** - Standardized access controls
- **Multi-Factor Authentication** - Enhanced security
- **Role-Based Access Control** - Granular permissions

### 4. Monitoring & Logging
- **Centralized Logging** - All logs sent to log archive account
- **CloudWatch Dashboards** - Real-time monitoring
- **Security Hub** - Security findings aggregation
- **Config Rules** - Compliance monitoring

## 🔄 Automation Workflows

### Account Provisioning (All Implementations)
```bash
cd projects/aws-landing-zone/automation

# Create new account
./create-account.sh -n "prod-app-01" -o "Workloads" -e "admin@company.com" -t workload

# Create development account
./create-account.sh -n "dev-app-01" -o "Sandbox" -e "developer@company.com" -t sandbox -p Developer

# Create security account
./create-account.sh -n "security-01" -o "Security" -e "security@company.com" -t security -p Administrator
```

### Account Management Features:
- ✅ **Validation** - Email format, OU existence, account uniqueness
- ✅ **Automated Setup** - Account creation, OU assignment, configuration
- ✅ **SSO Integration** - Permission set assignment, user access
- ✅ **Monitoring Setup** - CloudWatch dashboards, budget alerts
- ✅ **Documentation** - Automatic account documentation generation
- ✅ **Policy Application** - SCPs based on account type

## 🔐 Security Features (All Implementations)

### Guardrails
- **Preventive Guardrails** - Block non-compliant actions
- **Detective Guardrails** - Monitor and alert on violations
- **Custom Guardrails** - Organization-specific controls

### Security Policies
- **Password Policies** - Strong password requirements
- **MFA Enforcement** - Multi-factor authentication
- **Access Reviews** - Regular access audits
- **Privileged Access Management** - Elevated access controls

### Service Control Policies (SCPs)
- **Deny Root User** - Prevent root user access
- **Require MFA** - Enforce multi-factor authentication
- **Custom Policies** - Organization-specific controls

## 📊 Monitoring & Governance (All Implementations)

### Dashboards
- **Executive Dashboard** - High-level overview with account count and API calls
- **Security Dashboard** - Security metrics and Config rule evaluations
- **Compliance Dashboard** - Compliance status and violations
- **Cost Dashboard** - Cost optimization insights

### Alerting
- **Landing Zone Alerts** - General landing zone notifications
- **Security Alerts** - Security-related notifications
- **Compliance Alerts** - Compliance violation notifications
- **Budget Alerts** - Cost threshold notifications

## 💰 Cost Optimization (All Implementations)

### Cost Management
- **Budget Alerts** - Automated cost notifications at 80% and 100% thresholds
- **Cost Allocation Tags** - Automated resource tagging
- **Resource Optimization** - Automated resource right-sizing
- **Reserved Instance Management** - Cost savings optimization

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails**
   ```bash
   # Check prerequisites
   aws sts get-caller-identity
   aws organizations describe-organization
   
   # Validate templates
   # For CloudFormation:
   aws cloudformation validate-template --template-body file://main.json
   
   # For Terraform:
   terraform validate
   terraform plan
   ```

2. **Account Provisioning Issues**
   ```bash
   # Check account factory status
   aws organizations list-accounts
   
   # Validate account configuration
   aws organizations describe-account --account-id "123456789012"
   ```

3. **SSO Issues**
   ```bash
   # Check SSO status
   aws sso-admin list-instances
   
   # List permission sets
   aws sso-admin list-permission-sets --instance-arn <instance-arn>
   ```

### Debugging Commands
```bash
# Check organization status
aws organizations describe-organization

# List accounts
aws organizations list-accounts

# Check SSO status
aws sso-admin list-instances

# Monitor CloudTrail
aws logs describe-log-groups --log-group-name-prefix "aws-landing-zone"

# Check Config status
aws configservice describe-configuration-recorders

# Check CloudWatch dashboards
aws cloudwatch list-dashboards
```

## 📈 Comparison: Control Tower vs Terraform vs CloudFormation

| Feature | Control Tower | Terraform | CloudFormation |
|---------|---------------|-----------|----------------|
| **Setup Time** | 30-60 minutes | 15-30 minutes | 15-30 minutes |
| **Customization** | Limited | Full | Full |
| **Learning Curve** | Low | Medium | Medium |
| **AWS Native** | Yes | No | Yes |
| **Version Control** | Limited | Full | Full |
| **State Management** | AWS-managed | Terraform state | CloudFormation |
| **Cost** | Free | Free | Free |
| **Support** | AWS-managed | Community | AWS-managed |
| **Updates** | AWS-managed | Manual | Manual |
| **Best For** | Quick setup, AWS best practices | Full customization, IaC | AWS-native, JSON/YAML |

## 🔒 Security Best Practices

1. **Principle of Least Privilege**
   - Grant minimum required permissions
   - Regular access reviews
   - Automated permission cleanup

2. **Defense in Depth**
   - Multiple security layers
   - Network segmentation
   - Data encryption

3. **Continuous Monitoring**
   - Real-time security monitoring
   - Automated threat detection
   - Incident response automation

4. **Compliance Automation**
   - Automated compliance checks
   - Policy enforcement
   - Audit trail maintenance

## 📞 Support and Resources

### Documentation
- [AWS Control Tower User Guide](https://docs.aws.amazon.com/controltower/)
- [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/)
- [AWS SSO User Guide](https://docs.aws.amazon.com/singlesignon/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudFormation Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)

### Community Resources
- [AWS Landing Zone Community](https://github.com/aws-samples/aws-landing-zone)
- [AWS Control Tower Workshop](https://controltower.aws-management.tools/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

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
- Initial release with three implementation options
- AWS Control Tower automation
- Terraform implementation with full configuration
- CloudFormation implementation with deployment scripts
- Account provisioning automation
- Comprehensive security and compliance features
