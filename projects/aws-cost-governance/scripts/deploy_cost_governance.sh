#!/bin/bash

# AWS Cost Governance Deployment Script
# This script deploys the complete cost governance platform using Terraform

set -e

# Configuration
PROJECT_NAME="aws-cost-governance"
ENVIRONMENT="dev"
AWS_REGION="us-east-1"
TERRAFORM_DIR="terraform"
PYTHON_DIR="python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV     Environment (dev, staging, prod)"
    echo "  -r, --region REGION       AWS region"
    echo "  -p, --project-name NAME   Project name"
    echo "  -a, --alert-email EMAIL   Email for cost alerts"
    echo "  -b, --budget-email EMAIL  Email for budget alerts"
    echo "  -o, --report-email EMAIL  Email for optimization reports"
    echo "  -m, --monthly-budget AMT  Monthly budget limit in USD"
    echo "  -d, --daily-budget AMT    Daily budget limit in USD"
    echo "  -c, --ec2-budget AMT      EC2 budget limit in USD"
    echo "  -s, --s3-budget AMT       S3 budget limit in USD"
    echo "  -q, --rds-budget AMT      RDS budget limit in USD"
    echo "  -t, --daily-threshold AMT Daily cost threshold for alarms"
    echo "  -n, --monthly-threshold   Monthly cost threshold for alarms"
    echo "  -f, --dry-run             Show what would be deployed without deploying"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment prod --region us-west-2"
    echo "  $0 --alert-email admin@company.com --monthly-budget 5000"
    echo "  $0 --budget-email budget@company.com --report-email reports@company.com"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -a|--alert-email)
            ALERT_EMAIL="$2"
            shift 2
            ;;
        -b|--budget-email)
            BUDGET_EMAIL="$2"
            shift 2
            ;;
        -o|--report-email)
            REPORT_EMAIL="$2"
            shift 2
            ;;
        -m|--monthly-budget)
            MONTHLY_BUDGET="$2"
            shift 2
            ;;
        -d|--daily-budget)
            DAILY_BUDGET="$2"
            shift 2
            ;;
        -c|--ec2-budget)
            EC2_BUDGET="$2"
            shift 2
            ;;
        -s|--s3-budget)
            S3_BUDGET="$2"
            shift 2
            ;;
        -q|--rds-budget)
            RDS_BUDGET="$2"
            shift 2
            ;;
        -t|--daily-threshold)
            DAILY_THRESHOLD="$2"
            shift 2
            ;;
        -n|--monthly-threshold)
            MONTHLY_THRESHOLD="$2"
            shift 2
            ;;
        -f|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check jq
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install it first."
        exit 1
    fi
    
    print_success "Prerequisites check completed"
}

# Function to validate configuration
validate_configuration() {
    print_status "Validating configuration..."
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        print_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
        exit 1
    fi
    
    # Validate region
    if ! aws ec2 describe-regions --region-names "$AWS_REGION" &> /dev/null; then
        print_error "Invalid AWS region: $AWS_REGION"
        exit 1
    fi
    
    # Validate email addresses if provided
    if [[ -n "$ALERT_EMAIL" ]] && [[ ! "$ALERT_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid alert email address: $ALERT_EMAIL"
        exit 1
    fi
    
    if [[ -n "$BUDGET_EMAIL" ]] && [[ ! "$BUDGET_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid budget email address: $BUDGET_EMAIL"
        exit 1
    fi
    
    if [[ -n "$REPORT_EMAIL" ]] && [[ ! "$REPORT_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid report email address: $REPORT_EMAIL"
        exit 1
    fi
    
    # Validate budget amounts
    if [[ -n "$MONTHLY_BUDGET" ]] && [[ ! "$MONTHLY_BUDGET" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        print_error "Invalid monthly budget amount: $MONTHLY_BUDGET"
        exit 1
    fi
    
    if [[ -n "$DAILY_BUDGET" ]] && [[ ! "$DAILY_BUDGET" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        print_error "Invalid daily budget amount: $DAILY_BUDGET"
        exit 1
    fi
    
    print_success "Configuration validation completed"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [[ -f "$PYTHON_DIR/requirements.txt" ]]; then
        pip3 install -r "$PYTHON_DIR/requirements.txt"
        print_success "Python dependencies installed"
    else
        print_warning "No requirements.txt found, skipping Python dependency installation"
    fi
}

# Function to prepare Terraform
prepare_terraform() {
    print_status "Preparing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init
    
    # Create terraform.tfvars file
    cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
environment = "$ENVIRONMENT"
project_name = "$PROJECT_NAME"
log_retention_days = 14
create_budgets = true
create_cloudwatch_alarms = true
create_dashboards = true
create_anomaly_detection = true
create_cost_allocation_tags = true
create_lambda_functions = true
create_eventbridge_rules = true
create_s3_bucket = true
create_cost_usage_report = true
create_sns_topics = true
create_service_budgets = true
EOF

    # Add email configuration if provided
    if [[ -n "$ALERT_EMAIL" ]]; then
        echo "alert_email = \"$ALERT_EMAIL\"" >> terraform.tfvars
    fi
    
    if [[ -n "$BUDGET_EMAIL" ]]; then
        echo "budget_email = \"$BUDGET_EMAIL\"" >> terraform.tfvars
    fi
    
    if [[ -n "$REPORT_EMAIL" ]]; then
        echo "report_email = \"$REPORT_EMAIL\"" >> terraform.tfvars
    fi
    
    # Add budget configuration if provided
    if [[ -n "$MONTHLY_BUDGET" ]]; then
        echo "monthly_budget_limit = $MONTHLY_BUDGET" >> terraform.tfvars
    fi
    
    if [[ -n "$DAILY_BUDGET" ]]; then
        echo "daily_budget_limit = $DAILY_BUDGET" >> terraform.tfvars
    fi
    
    if [[ -n "$EC2_BUDGET" ]]; then
        echo "ec2_budget_limit = $EC2_BUDGET" >> terraform.tfvars
    fi
    
    if [[ -n "$S3_BUDGET" ]]; then
        echo "s3_budget_limit = $S3_BUDGET" >> terraform.tfvars
    fi
    
    if [[ -n "$RDS_BUDGET" ]]; then
        echo "rds_budget_limit = $RDS_BUDGET" >> terraform.tfvars
    fi
    
    # Add threshold configuration if provided
    if [[ -n "$DAILY_THRESHOLD" ]]; then
        echo "daily_cost_threshold = $DAILY_THRESHOLD" >> terraform.tfvars
    fi
    
    if [[ -n "$MONTHLY_THRESHOLD" ]]; then
        echo "monthly_cost_threshold = $MONTHLY_THRESHOLD" >> terraform.tfvars
    fi
    
    print_success "Terraform prepared"
}

# Function to plan Terraform deployment
plan_terraform() {
    print_status "Planning Terraform deployment..."
    
    terraform plan -out=tfplan
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_success "Dry run completed. No resources were deployed."
        exit 0
    fi
}

# Function to apply Terraform deployment
apply_terraform() {
    print_status "Applying Terraform deployment..."
    
    terraform apply tfplan
    
    print_success "Terraform deployment completed"
}

# Function to create Lambda deployment package
create_lambda_package() {
    print_status "Creating Lambda deployment package..."
    
    # Create temporary directory for Lambda package
    mkdir -p temp_lambda_package
    
    # Create cost automation Lambda function
    cat > temp_lambda_package/cost_automation.py << 'EOF'
import json
import boto3
import os
from datetime import datetime, timedelta

def handler(event, context):
    """
    Cost automation Lambda function
    """
    try:
        # Get environment variables
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        budget_topic_arn = os.environ.get('BUDGET_TOPIC_ARN')
        report_topic_arn = os.environ.get('REPORT_TOPIC_ARN')
        
        # Initialize AWS clients
        ce_client = boto3.client('ce')
        sns_client = boto3.client('sns')
        budgets_client = boto3.client('budgets')
        
        # Get current cost
        today = datetime.now().strftime('%Y-%m-%d')
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': today, 'End': today},
            Granularity='DAILY',
            Metrics=['BlendedCost']
        )
        
        current_cost = 0
        for result in response.get('ResultsByTime', []):
            current_cost += float(result['Total']['BlendedCost']['Amount'])
        
        # Send cost alert if threshold exceeded
        if current_cost > 100:  # $100 daily threshold
            message = f"Daily cost ${current_cost:.2f} exceeds threshold of $100"
            if sns_topic_arn:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=message,
                    Subject="AWS Cost Alert"
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cost automation completed successfully',
                'current_cost': current_cost,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in cost automation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Cost automation failed',
                'message': str(e)
            })
        }
EOF

    # Create zip file
    cd temp_lambda_package
    zip -r ../cost_automation.zip .
    cd ..
    
    print_success "Lambda deployment package created"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get outputs from Terraform
    SNS_TOPICS=$(terraform output -json sns_topics 2>/dev/null || echo "{}")
    BUDGETS=$(terraform output -json budgets 2>/dev/null || echo "{}")
    DASHBOARD=$(terraform output -json cloudwatch_dashboard 2>/dev/null || echo "{}")
    
    # Test SNS topics
    if [[ "$SNS_TOPICS" != "{}" ]]; then
        print_status "Testing SNS topics..."
        cost_alerts_arn=$(echo "$SNS_TOPICS" | jq -r '.cost_alerts.arn // empty')
        if [[ -n "$cost_alerts_arn" ]]; then
            print_success "Cost alerts SNS topic created: $cost_alerts_arn"
        fi
    fi
    
    # Test budgets
    if [[ "$BUDGETS" != "{}" ]]; then
        print_status "Testing budgets..."
        monthly_budget=$(echo "$BUDGETS" | jq -r '.monthly_budget.name // empty')
        if [[ -n "$monthly_budget" ]]; then
            print_success "Monthly budget created: $monthly_budget"
        fi
    fi
    
    # Test dashboard
    if [[ "$DASHBOARD" != "{}" ]]; then
        print_status "Testing CloudWatch dashboard..."
        dashboard_name=$(echo "$DASHBOARD" | jq -r '.dashboard.name // empty')
        if [[ -n "$dashboard_name" ]]; then
            print_success "CloudWatch dashboard created: $dashboard_name"
        fi
    fi
    
    print_success "Deployment testing completed"
}

# Function to display deployment summary
display_summary() {
    print_success "AWS Cost Governance deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Project Name: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "AWS Region: $AWS_REGION"
    echo ""
    
    # Get outputs from Terraform
    cd "$TERRAFORM_DIR"
    
    echo "=== Resources Created ==="
    
    # SNS topics
    SNS_TOPICS=$(terraform output -json sns_topics 2>/dev/null || echo "{}")
    if [[ "$SNS_TOPICS" != "{}" ]]; then
        echo "SNS Topics:"
        echo "$SNS_TOPICS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # Budgets
    BUDGETS=$(terraform output -json budgets 2>/dev/null || echo "{}")
    if [[ "$BUDGETS" != "{}" ]]; then
        echo "Budgets:"
        echo "$BUDGETS" | jq -r 'to_entries[] | "  - \(.key): $\(.value.limit) \(.value.unit)"'
    fi
    
    # CloudWatch alarms
    ALARMS=$(terraform output -json cloudwatch_alarms 2>/dev/null || echo "{}")
    if [[ "$ALARMS" != "{}" ]]; then
        echo "CloudWatch Alarms:"
        echo "$ALARMS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # Lambda functions
    LAMBDA=$(terraform output -json lambda_functions 2>/dev/null || echo "{}")
    if [[ "$LAMBDA" != "{}" ]]; then
        echo "Lambda Functions:"
        echo "$LAMBDA" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    echo ""
    echo "=== Cost Governance Features ==="
    echo "✅ Budget Management - Automated budget creation and monitoring"
    echo "✅ Cost Alerts - Real-time cost threshold alerts"
    echo "✅ Anomaly Detection - Automated detection of unusual spending"
    echo "✅ Cost Allocation - Tag-based cost allocation and reporting"
    echo "✅ Optimization Recommendations - Automated cost optimization"
    echo "✅ Resource Rightsizing - Identify rightsizing opportunities"
    echo "✅ Reserved Instances - RI purchase recommendations"
    echo "✅ Savings Plans - SP recommendations and management"
    echo "✅ Unused Resource Cleanup - Identify and clean up unused resources"
    echo "✅ Automated Reporting - Scheduled cost and optimization reports"
    echo "✅ Cost Forecasting - Predict future costs"
    echo "✅ Multi-Account Support - Cost governance across accounts"
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Configure email subscriptions for SNS topics"
    echo "2. Review and adjust budget thresholds"
    echo "3. Set up cost allocation tags on resources"
    echo "4. Enable Cost and Usage Reports"
    echo "5. Configure anomaly detection thresholds"
    echo "6. Review CloudWatch dashboard"
    echo "7. Set up automated optimization workflows"
    echo "8. Configure resource tagging policies"
    echo "9. Review optimization recommendations"
    echo "10. Set up cross-account governance if needed"
    
    echo ""
    echo "=== Important URLs ==="
    echo "Cost Explorer: https://console.aws.amazon.com/cost-management/home?region=$AWS_REGION#/dashboard"
    echo "Budgets: https://console.aws.amazon.com/billing/home?region=$AWS_REGION#/budgets"
    echo "CloudWatch: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION"
    echo "Cost Anomaly Detection: https://console.aws.amazon.com/cost-management/home?region=$AWS_REGION#/anomaly-detection"
    echo "Cost Allocation Tags: https://console.aws.amazon.com/cost-management/home?region=$AWS_REGION#/cost-categories"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary Lambda package
    rm -rf temp_lambda_package
    rm -f cost_automation.zip
    
    # Remove Terraform plan file
    cd "$TERRAFORM_DIR"
    rm -f tfplan
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Cost Governance Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    validate_configuration
    install_python_dependencies
    create_lambda_package
    prepare_terraform
    plan_terraform
    apply_terraform
    test_deployment
    display_summary
    cleanup
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"