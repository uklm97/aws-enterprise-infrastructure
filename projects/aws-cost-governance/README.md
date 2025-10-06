# AWS Cost Governance Platform

A comprehensive cost governance platform for AWS with advanced budget management, cost optimization, monitoring, and automation capabilities. This platform provides enterprise-grade cost control, optimization recommendations, and automated cost management workflows.

## 🏗️ Architecture Overview

### Core Components
- **Budget Management** - Multi-level budgets with automated alerts and notifications
- **Cost Monitoring** - Real-time cost tracking with CloudWatch integration
- **Anomaly Detection** - AI-powered detection of unusual spending patterns
- **Cost Allocation** - Tag-based cost allocation and detailed reporting
- **Optimization Engine** - Automated recommendations for cost savings
- **Resource Rightsizing** - Intelligent resource optimization suggestions
- **Reserved Instances** - RI purchase and utilization recommendations
- **Savings Plans** - SP recommendations and management
- **Automated Cleanup** - Unused resource identification and cleanup
- **Cost Forecasting** - Predictive cost analysis and budgeting

### Cost Governance Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cost Explorer │───▶│  Budget Manager │───▶│  Cost Optimizer │
│   (Data Source) │    │  (Control)      │    │  (Actions)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Cost Monitor   │              │
         │              │  (Alerts)       │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Anomaly        │    │  Cost           │    │  Resource       │
│  Detection      │    │  Allocation     │    │  Rightsizing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
aws-cost-governance/
├── README.md                           # This documentation
├── requirements.txt                    # Python dependencies
├── python/                             # Python automation modules
│   ├── budget/
│   │   └── budget_manager.py          # Budget management and alerts
│   ├── optimization/
│   │   └── cost_optimizer.py          # Cost optimization engine
│   ├── monitoring/
│   │   └── cost_monitor.py            # Cost monitoring and dashboards
│   └── automation/
│       └── cost_automation.py         # Automated cost management
├── terraform/                          # Terraform infrastructure
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Terraform variables
│   └── outputs.tf                     # Terraform outputs
└── scripts/                           # Deployment and utility scripts
    └── deploy_cost_governance.sh      # Automated deployment script
```

## 🚀 Quick Start

### Prerequisites
1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** (>= 1.0) installed
4. **Python 3.8+** installed
5. **jq** for JSON processing

### Option 1: Automated Deployment (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd aws-cost-governance

# Run the deployment script
./scripts/deploy_cost_governance.sh --environment dev --region us-east-1

# With email configuration
./scripts/deploy_cost_governance.sh \
  --environment prod \
  --region us-west-2 \
  --alert-email admin@company.com \
  --budget-email budget@company.com \
  --report-email reports@company.com \
  --monthly-budget 5000 \
  --daily-budget 200
```

### Option 2: Manual Terraform Deployment
```bash
cd terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars << EOF
aws_region = "us-east-1"
environment = "dev"
project_name = "aws-cost-governance"
alert_email = "admin@company.com"
budget_email = "budget@company.com"
report_email = "reports@company.com"
monthly_budget_limit = 1000
daily_budget_limit = 50
EOF

# Plan and apply
terraform plan
terraform apply
```

## 🛠️ Features

### Budget Management
- **Multi-Level Budgets** - Account, service, and project-level budgets
- **Automated Alerts** - Email and SNS notifications at configurable thresholds
- **Budget Tracking** - Real-time budget vs. actual spending monitoring
- **Forecast Integration** - Predictive budget planning based on historical data
- **Custom Thresholds** - Flexible alert thresholds (50%, 80%, 100%, etc.)

### Cost Monitoring
- **Real-Time Dashboards** - CloudWatch dashboards with cost metrics
- **Service-Level Monitoring** - Cost tracking by AWS service
- **Tag-Based Analysis** - Cost allocation by tags and categories
- **Trend Analysis** - Historical cost trends and patterns
- **Anomaly Detection** - AI-powered detection of unusual spending

### Cost Optimization
- **Rightsizing Recommendations** - Optimal instance sizing suggestions
- **Reserved Instance Analysis** - RI purchase and utilization recommendations
- **Savings Plans Optimization** - SP recommendations for maximum savings
- **Unused Resource Cleanup** - Automated identification of unused resources
- **Spot Instance Recommendations** - Cost-effective spot instance suggestions

### Cost Allocation
- **Tag-Based Allocation** - Cost distribution by resource tags
- **Cost Categories** - Custom cost categorization and reporting
- **Multi-Account Support** - Cross-account cost allocation
- **Departmental Billing** - Cost allocation by department or team
- **Project Cost Tracking** - Project-level cost visibility

### Automation
- **Scheduled Reports** - Automated daily, weekly, and monthly reports
- **Cost Alerts** - Automated alerting on cost thresholds
- **Optimization Workflows** - Automated cost optimization actions
- **Resource Cleanup** - Scheduled cleanup of unused resources
- **Budget Adjustments** - Automated budget adjustments based on trends

## 📊 Monitoring & Observability

### CloudWatch Integration
- **Custom Dashboards** - Real-time cost monitoring dashboards
- **Cost Alarms** - Automated alerting on cost thresholds
- **Custom Metrics** - Application-specific cost metrics
- **Log Aggregation** - Centralized cost-related logging

### Cost Analytics
- **Cost Trends** - Historical cost analysis and trending
- **Forecasting** - Predictive cost modeling
- **Variance Analysis** - Budget vs. actual cost analysis
- **ROI Tracking** - Return on investment for cost optimizations

### Reporting
- **Scheduled Reports** - Automated cost and optimization reports
- **Custom Reports** - Configurable report generation
- **Export Capabilities** - CSV, JSON, and Excel export options
- **Dashboard Sharing** - Shareable cost dashboards

## 🔒 Security & Compliance

### Access Control
- **IAM Integration** - Role-based access control
- **Resource Policies** - Fine-grained cost governance permissions
- **Multi-Account Support** - Cross-account cost governance
- **Audit Logging** - Comprehensive audit trails

### Data Protection
- **Encryption** - Data encryption at rest and in transit
- **Data Retention** - Configurable data retention policies
- **Privacy Controls** - Sensitive data protection
- **Compliance** - SOC2, HIPAA, and other compliance support

## 💰 Cost Optimization Features

### Automated Recommendations
- **Rightsizing** - Up to 30% savings through optimal sizing
- **Reserved Instances** - Up to 75% savings on predictable workloads
- **Savings Plans** - Up to 72% savings on compute usage
- **Spot Instances** - Up to 90% savings for fault-tolerant workloads
- **Storage Optimization** - Up to 50% savings with intelligent tiering

### Cost Governance
- **Budget Enforcement** - Automated budget controls
- **Spending Limits** - Hard and soft spending limits
- **Approval Workflows** - Cost approval processes
- **Policy Enforcement** - Automated policy compliance

### Resource Management
- **Unused Resource Detection** - Identify and clean up unused resources
- **Lifecycle Management** - Automated resource lifecycle management
- **Tagging Policies** - Enforce resource tagging for cost allocation
- **Resource Optimization** - Continuous resource optimization

## 🔧 Configuration Options

### Environment Variables
```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# Cost Governance Configuration
export ENVIRONMENT=dev
export PROJECT_NAME=aws-cost-governance

# Email Configuration
export ALERT_EMAIL=admin@company.com
export BUDGET_EMAIL=budget@company.com
export REPORT_EMAIL=reports@company.com

# Budget Configuration
export MONTHLY_BUDGET_LIMIT=1000
export DAILY_BUDGET_LIMIT=50
export EC2_BUDGET_LIMIT=500
export RDS_BUDGET_LIMIT=200
export S3_BUDGET_LIMIT=100
```

### Terraform Variables
```hcl
# Core settings
aws_region = "us-east-1"
environment = "dev"
project_name = "aws-cost-governance"

# Budget settings
monthly_budget_limit = 1000
daily_budget_limit = 50
ec2_budget_limit = 500
rds_budget_limit = 200
s3_budget_limit = 100

# Alert settings
alert_email = "admin@company.com"
budget_email = "budget@company.com"
report_email = "reports@company.com"

# Feature flags
create_budgets = true
create_cloudwatch_alarms = true
create_dashboards = true
create_anomaly_detection = true
create_cost_allocation_tags = true
create_lambda_functions = true
create_eventbridge_rules = true
```

## 🧪 Testing

### Unit Tests
```bash
cd python
python -m pytest tests/unit/ -v
```

### Integration Tests
```bash
cd python
python -m pytest tests/integration/ -v
```

### Cost Analysis Tests
```bash
# Test cost optimization recommendations
python scripts/test_cost_optimization.py

# Test budget management
python scripts/test_budget_management.py

# Test anomaly detection
python scripts/test_anomaly_detection.py
```

## 📈 Performance Optimization

### Cost Analysis Performance
- **Parallel Processing** - Multi-threaded cost analysis
- **Caching** - Intelligent caching of cost data
- **Incremental Updates** - Delta cost analysis
- **Batch Processing** - Efficient batch operations

### Resource Optimization
- **Machine Learning** - ML-based optimization recommendations
- **Pattern Recognition** - Usage pattern analysis
- **Predictive Analytics** - Future cost predictions
- **Automated Actions** - Automated optimization actions

## 🚨 Troubleshooting

### Common Issues

1. **Budget Alerts Not Working**
   ```bash
   # Check SNS topic subscriptions
   aws sns list-subscriptions-by-topic --topic-arn <topic-arn>
   
   # Verify email confirmation
   # Check email for SNS subscription confirmation
   ```

2. **Cost Data Not Available**
   ```bash
   # Check Cost Explorer permissions
   aws ce get-cost-and-usage --time-period Start=2023-01-01,End=2023-01-31
   
   # Verify billing permissions
   aws iam get-user
   ```

3. **Anomaly Detection Issues**
   ```bash
   # Check anomaly detector status
   aws ce describe-anomaly-detectors
   
   # Verify data availability
   aws ce get-anomalies --date-interval Start=2023-01-01,End=2023-01-31
   ```

### Debugging Commands
```bash
# Check budget status
aws budgets describe-budgets --account-id <account-id>

# Monitor cost trends
aws ce get-cost-and-usage \
  --time-period Start=2023-01-01,End=2023-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Check CloudWatch alarms
aws cloudwatch describe-alarms --alarm-names <alarm-name>

# Verify SNS topics
aws sns list-topics
```

## 📚 Documentation

### API Documentation
- **Cost Explorer API** - AWS Cost Explorer integration
- **Budgets API** - AWS Budgets management
- **CloudWatch API** - Monitoring and alerting
- **SNS API** - Notification management

### Architecture Documentation
- **System Design** - Detailed architecture diagrams
- **Data Flow** - Cost data flow documentation
- **Security Model** - Security architecture and controls
- **Integration Guide** - Third-party integrations

### Operations Documentation
- **Deployment Guide** - Step-by-step deployment instructions
- **Configuration Guide** - Configuration options and settings
- **Monitoring Guide** - Monitoring setup and configuration
- **Troubleshooting Guide** - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation** - Check the comprehensive documentation
- **Issues** - Open an issue on GitHub
- **Discussions** - Use GitHub Discussions for questions
- **Email** - Contact the development team

## 🔄 Changelog

### Version 1.0.0
- Initial release with complete cost governance platform
- Budget management with automated alerts
- Cost monitoring and dashboards
- Anomaly detection and alerting
- Cost allocation and tagging
- Optimization recommendations engine
- Resource rightsizing suggestions
- Reserved Instance recommendations
- Savings Plans optimization
- Unused resource cleanup
- Automated cost reporting
- Cost forecasting and prediction
- Multi-account support
- Terraform infrastructure
- Comprehensive documentation