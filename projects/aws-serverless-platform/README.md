# AWS Serverless Platform

A comprehensive serverless platform built on AWS services including Lambda, DynamoDB, SQS, SNS, Step Functions, and API Gateway. This platform provides a complete, production-ready serverless infrastructure with monitoring, security, and cost optimization features.

## 🏗️ Architecture Overview

### Core Components
- **Lambda Functions** - Serverless compute with Python runtime
- **DynamoDB** - NoSQL database with global secondary indexes and streams
- **SQS** - Message queuing with dead letter queues and FIFO support
- **SNS** - Pub/sub messaging with email notifications and topic filtering
- **Step Functions** - Workflow orchestration with error handling and retries
- **API Gateway** - RESTful API endpoints with CORS and authentication
- **CloudWatch** - Comprehensive monitoring and logging
- **X-Ray** - Distributed tracing and performance analysis

### Serverless Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│  Lambda Function│───▶│    DynamoDB     │
│   (REST API)    │    │  (Order Proc.)  │    │   (Users/Orders)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Step Functions │              │
         │              │  (Workflow)     │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SNS Topics    │    │   SQS Queues    │    │  CloudWatch     │
│ (Notifications) │    │ (Processing)    │    │ (Monitoring)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
aws-serverless-platform/
├── README.md                           # This documentation
├── requirements.txt                    # Python dependencies
├── python/                             # Python automation modules
│   ├── lambda/
│   │   └── lambda_manager.py          # Lambda function management
│   ├── api_gateway/
│   │   └── api_manager.py             # API Gateway management
│   ├── dynamodb/
│   │   └── dynamodb_manager.py        # DynamoDB management
│   ├── step_functions/
│   │   └── step_functions_manager.py  # Step Functions management
│   └── sqs_sns/
│       └── sqs_sns_manager.py         # SQS and SNS management
├── terraform/                          # Terraform infrastructure
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Terraform variables
│   └── outputs.tf                     # Terraform outputs
├── cloudformation/                     # CloudFormation templates
│   └── serverless-platform.json       # Complete CloudFormation template
└── scripts/                           # Deployment and utility scripts
    └── deploy_serverless.sh           # Automated deployment script
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
cd aws-serverless-platform

# Run the deployment script
./scripts/deploy_serverless.sh --environment dev --region us-east-1

# With VPC configuration
./scripts/deploy_serverless.sh \
  --environment prod \
  --region us-west-2 \
  --vpc-id vpc-12345678 \
  --subnet-ids subnet-123,subnet-456 \
  --notification-email admin@company.com \
  --alert-email alerts@company.com
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
project_name = "aws-serverless-platform"
notification_email = "admin@company.com"
alert_email = "alerts@company.com"
EOF

# Plan and apply
terraform plan
terraform apply
```

### Option 3: CloudFormation Deployment
```bash
# Deploy using AWS CLI
aws cloudformation create-stack \
  --stack-name serverless-platform \
  --template-body file://cloudformation/serverless-platform.json \
  --parameters ParameterKey=ProjectName,ParameterValue=aws-serverless-platform \
               ParameterKey=Environment,ParameterValue=dev \
               ParameterKey=NotificationEmail,ParameterValue=admin@company.com \
  --capabilities CAPABILITY_IAM
```

## 🛠️ Features

### Lambda Functions
- **Order Processor** - Processes incoming orders and stores them in DynamoDB
- **Notification Sender** - Sends notifications via SNS
- **Auto-scaling** - Automatically scales based on demand
- **Dead Letter Queues** - Handles failed message processing
- **VPC Support** - Can run in VPC for enhanced security

### DynamoDB Tables
- **Users Table** - User information with GSI on email and created_at
- **Orders Table** - Order data with GSI on user_id and status
- **Point-in-time Recovery** - Automated backups and recovery
- **Global Secondary Indexes** - Optimized query performance
- **Streams** - Real-time data change notifications

### SQS Queues
- **Order Processing Queue** - Main processing queue
- **Dead Letter Queue** - Failed message handling
- **FIFO Support** - Message ordering when needed
- **Visibility Timeout** - Prevents duplicate processing
- **Long Polling** - Reduces API calls and costs

### SNS Topics
- **Order Notifications** - Customer notifications
- **System Alerts** - Operational alerts
- **Email Subscriptions** - Email-based notifications
- **Topic Filtering** - Message filtering based on attributes

### Step Functions
- **Order Workflow** - Complete order processing workflow
- **Error Handling** - Retry logic and error recovery
- **Parallel Processing** - Concurrent task execution
- **Conditional Logic** - Dynamic workflow paths

### API Gateway
- **REST API** - RESTful endpoints for order management
- **CORS Support** - Cross-origin resource sharing
- **Request/Response Transformation** - Data format conversion
- **Rate Limiting** - API throttling and quotas

## 📊 Monitoring & Observability

### CloudWatch Integration
- **Custom Dashboards** - Real-time system metrics
- **Alarms** - Automated alerting on thresholds
- **Log Aggregation** - Centralized logging
- **Custom Metrics** - Application-specific metrics

### X-Ray Tracing
- **Distributed Tracing** - End-to-end request tracking
- **Performance Analysis** - Bottleneck identification
- **Service Map** - Visual service dependencies
- **Error Tracking** - Failed request analysis

### Monitoring Features
- **Lambda Metrics** - Invocations, errors, duration, throttles
- **DynamoDB Metrics** - Read/write capacity, throttles, item count
- **SQS Metrics** - Queue depth, message age, processing time
- **SNS Metrics** - Message delivery, failures, bounces
- **API Gateway Metrics** - Request count, latency, error rates

## 🔒 Security Features

### Encryption
- **KMS Integration** - Customer-managed encryption keys
- **Data at Rest** - DynamoDB, S3, and Lambda encryption
- **Data in Transit** - TLS/SSL for all communications
- **Key Rotation** - Automatic key rotation

### Access Control
- **IAM Roles** - Least privilege access
- **Resource Policies** - Fine-grained permissions
- **VPC Configuration** - Network isolation
- **API Authentication** - Optional API key authentication

### Compliance
- **Audit Logging** - CloudTrail integration
- **Data Classification** - Sensitive data handling
- **Retention Policies** - Data lifecycle management
- **Backup & Recovery** - Point-in-time recovery

## 💰 Cost Optimization

### Pay-per-Request Pricing
- **Lambda** - Pay only for compute time used
- **DynamoDB** - On-demand billing for unpredictable workloads
- **SQS/SNS** - Pay per message processed
- **API Gateway** - Pay per API call

### Auto-scaling
- **Automatic Scaling** - Scales based on demand
- **Cost Alerts** - Budget monitoring and alerts
- **Resource Optimization** - Right-sizing recommendations
- **Reserved Capacity** - Optional reserved pricing for predictable workloads

### Cost Management
- **Cost Allocation Tags** - Resource cost tracking
- **Budget Alerts** - Automated cost notifications
- **Usage Reports** - Detailed cost breakdowns
- **Optimization Recommendations** - AWS Cost Explorer insights

## 🔧 Configuration Options

### Environment Variables
```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# Platform Configuration
export ENVIRONMENT=dev
export PROJECT_NAME=aws-serverless-platform

# Notification Settings
export NOTIFICATION_EMAIL=admin@company.com
export ALERT_EMAIL=alerts@company.com

# VPC Configuration (optional)
export VPC_ID=vpc-12345678
export SUBNET_IDS=subnet-123,subnet-456
```

### Terraform Variables
```hcl
# Core settings
aws_region = "us-east-1"
environment = "dev"
project_name = "aws-serverless-platform"

# Feature flags
create_dynamodb_tables = true
create_sqs_queues = true
create_sns_topics = true
create_lambda_functions = true
create_step_functions = true
create_api_gateway = true

# Security settings
enable_encryption = true
enable_xray_tracing = true
enable_point_in_time_recovery = true

# Monitoring settings
log_retention_days = 14
create_cloudwatch_alarms = true
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

### Load Testing
```bash
# Using the provided load testing script
python scripts/load_test.py --endpoint https://api.example.com/orders
```

### Security Testing
```bash
# Run security scans
python scripts/security_scan.py
```

## 📈 Performance Optimization

### Lambda Optimization
- **Memory Tuning** - Optimize memory allocation
- **Cold Start Reduction** - Provisioned concurrency
- **Package Size** - Minimize deployment packages
- **Connection Pooling** - Reuse database connections

### DynamoDB Optimization
- **Partition Key Design** - Even data distribution
- **GSI Optimization** - Efficient query patterns
- **Batch Operations** - Reduce API calls
- **Caching** - DAX for microsecond latency

### API Gateway Optimization
- **Caching** - Response caching
- **Compression** - Gzip compression
- **Request Validation** - Early request validation
- **Rate Limiting** - Prevent abuse

## 🚨 Troubleshooting

### Common Issues

1. **Lambda Timeout Errors**
   ```bash
   # Check CloudWatch logs
   aws logs describe-log-groups --log-group-name-prefix "/aws/lambda"
   
   # Increase timeout in Terraform
   lambda_timeout = 900  # 15 minutes
   ```

2. **DynamoDB Throttling**
   ```bash
   # Check throttled requests
   aws cloudwatch get-metric-statistics \
     --namespace AWS/DynamoDB \
     --metric-name ThrottledRequests \
     --start-time 2023-01-01T00:00:00Z \
     --end-time 2023-01-02T00:00:00Z \
     --period 3600 \
     --statistics Sum
   ```

3. **API Gateway CORS Issues**
   ```bash
   # Enable CORS in API Gateway
   aws apigateway put-integration-response \
     --rest-api-id <api-id> \
     --resource-id <resource-id> \
     --http-method OPTIONS \
     --status-code 200 \
     --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}'
   ```

### Debugging Commands
```bash
# Check Lambda function status
aws lambda get-function --function-name <function-name>

# Monitor DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check SQS queue attributes
aws sqs get-queue-attributes \
  --queue-url <queue-url> \
  --attribute-names All

# Monitor Step Functions executions
aws stepfunctions list-executions \
  --state-machine-arn <state-machine-arn>
```

## 📚 Documentation

### API Documentation
- **OpenAPI Specification** - Available at `/docs` endpoint
- **Postman Collection** - Import for testing
- **Example Requests** - cURL examples provided

### Architecture Documentation
- **System Design** - Detailed architecture diagrams
- **Data Flow** - Request/response flow documentation
- **Security Model** - Security architecture and controls

### Operations Documentation
- **Deployment Guide** - Step-by-step deployment instructions
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
- Initial release with complete serverless platform
- Lambda functions with Python automation
- DynamoDB tables with GSI and streams
- SQS queues with DLQ support
- SNS topics with email notifications
- Step Functions workflow orchestration
- API Gateway REST API
- CloudWatch monitoring and alerting
- X-Ray distributed tracing
- Terraform and CloudFormation templates
- Automated deployment scripts
- Comprehensive documentation