#!/bin/bash

# AWS Serverless Platform Deployment Script
# This script deploys the complete serverless platform using Terraform

set -e

# Configuration
PROJECT_NAME="aws-serverless-platform"
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
    echo "  -v, --vpc-id VPC_ID       VPC ID for Lambda functions"
    echo "  -s, --subnet-ids SUBNETS  Comma-separated subnet IDs"
    echo "  -n, --notification-email  Email for notifications"
    echo "  -a, --alert-email         Email for system alerts"
    echo "  -d, --dry-run             Show what would be deployed without deploying"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment prod --region us-west-2"
    echo "  $0 --vpc-id vpc-12345678 --subnet-ids subnet-123,subnet-456"
    echo "  $0 --notification-email admin@company.com --alert-email alerts@company.com"
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
        -v|--vpc-id)
            VPC_ID="$2"
            shift 2
            ;;
        -s|--subnet-ids)
            SUBNET_IDS="$2"
            shift 2
            ;;
        -n|--notification-email)
            NOTIFICATION_EMAIL="$2"
            shift 2
            ;;
        -a|--alert-email)
            ALERT_EMAIL="$2"
            shift 2
            ;;
        -d|--dry-run)
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
    
    # Validate VPC if provided
    if [[ -n "$VPC_ID" ]]; then
        if ! aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --region "$AWS_REGION" &> /dev/null; then
            print_error "Invalid VPC ID: $VPC_ID"
            exit 1
        fi
    fi
    
    # Validate subnets if provided
    if [[ -n "$SUBNET_IDS" ]]; then
        IFS=',' read -ra SUBNET_ARRAY <<< "$SUBNET_IDS"
        for subnet in "${SUBNET_ARRAY[@]}"; do
            if ! aws ec2 describe-subnets --subnet-ids "$subnet" --region "$AWS_REGION" &> /dev/null; then
                print_error "Invalid subnet ID: $subnet"
                exit 1
            fi
        done
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
enable_xray_tracing = true
enable_encryption = true
create_dynamodb_tables = true
create_sqs_queues = true
create_sns_topics = true
create_lambda_functions = true
create_step_functions = true
create_api_gateway = true
create_cloudwatch_alarms = true
create_eventbridge_rules = true
EOF

    # Add VPC configuration if provided
    if [[ -n "$VPC_ID" ]]; then
        echo "vpc_id = \"$VPC_ID\"" >> terraform.tfvars
    fi
    
    if [[ -n "$SUBNET_IDS" ]]; then
        echo "vpc_subnet_ids = [\"$(echo $SUBNET_IDS | sed 's/,/", "/g')\"]" >> terraform.tfvars
    fi
    
    # Add email configuration if provided
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        echo "notification_email = \"$NOTIFICATION_EMAIL\"" >> terraform.tfvars
    fi
    
    if [[ -n "$ALERT_EMAIL" ]]; then
        echo "alert_email = \"$ALERT_EMAIL\"" >> terraform.tfvars
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

# Function to create Lambda deployment packages
create_lambda_packages() {
    print_status "Creating Lambda deployment packages..."
    
    # Create temporary directory for Lambda packages
    mkdir -p temp_lambda_packages
    
    # Create order processor Lambda package
    cat > temp_lambda_packages/order_processor.py << 'EOF'
import json
import boto3
import os

def handler(event, context):
    """
    Order processor Lambda function
    """
    try:
        # Get environment variables
        dynamodb_table = os.environ.get('DYNAMODB_TABLE')
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        
        # Initialize AWS clients
        dynamodb = boto3.resource('dynamodb')
        sns = boto3.client('sns')
        
        # Process the order
        order_data = event.get('order', {})
        
        if dynamodb_table:
            table = dynamodb.Table(dynamodb_table)
            # Store order in DynamoDB
            table.put_item(Item=order_data)
        
        if sns_topic_arn:
            # Send notification
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=f"Order processed: {order_data.get('order_id', 'unknown')}",
                Subject="Order Processed"
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Order processed successfully',
                'order_id': order_data.get('order_id')
            })
        }
        
    except Exception as e:
        print(f"Error processing order: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process order',
                'message': str(e)
            })
        }
EOF

    # Create notification sender Lambda package
    cat > temp_lambda_packages/notification_sender.py << 'EOF'
import json
import boto3
import os

def handler(event, context):
    """
    Notification sender Lambda function
    """
    try:
        # Get environment variables
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        
        if not sns_topic_arn:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'SNS topic ARN not configured'})
            }
        
        # Initialize SNS client
        sns = boto3.client('sns')
        
        # Send notification
        message = event.get('message', 'Notification sent')
        subject = event.get('subject', 'System Notification')
        
        response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=subject
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notification sent successfully',
                'message_id': response['MessageId']
            })
        }
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to send notification',
                'message': str(e)
            })
        }
EOF

    # Create zip files
    cd temp_lambda_packages
    
    # Order processor package
    zip -r ../order_processor.zip order_processor.py
    
    # Notification sender package
    zip -r ../notification_sender.zip notification_sender.py
    
    cd ..
    
    print_success "Lambda deployment packages created"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get outputs from Terraform
    API_GATEWAY_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
    LAMBDA_FUNCTIONS=$(terraform output -json lambda_functions 2>/dev/null || echo "{}")
    
    if [[ -n "$API_GATEWAY_URL" ]]; then
        print_status "Testing API Gateway endpoint..."
        
        # Test API Gateway endpoint
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_GATEWAY_URL/orders" -X POST -H "Content-Type: application/json" -d '{"test": "data"}' || echo "000")
        
        if [[ "$response" == "200" ]]; then
            print_success "API Gateway test passed"
        else
            print_warning "API Gateway test failed with status: $response"
        fi
    fi
    
    # Test Lambda functions
    if [[ "$LAMBDA_FUNCTIONS" != "{}" ]]; then
        print_status "Testing Lambda functions..."
        
        # Get function names from Terraform output
        ORDER_PROCESSOR=$(echo "$LAMBDA_FUNCTIONS" | jq -r '.order_processor.name // empty')
        
        if [[ -n "$ORDER_PROCESSOR" ]]; then
            # Test Lambda function
            aws lambda invoke \
                --function-name "$ORDER_PROCESSOR" \
                --payload '{"order": {"order_id": "test-123", "status": "processing"}}' \
                --region "$AWS_REGION" \
                /tmp/lambda_test_response.json
            
            if [[ $? -eq 0 ]]; then
                print_success "Lambda function test passed"
            else
                print_warning "Lambda function test failed"
            fi
        fi
    fi
    
    print_success "Deployment testing completed"
}

# Function to display deployment summary
display_summary() {
    print_success "AWS Serverless Platform deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Project Name: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "AWS Region: $AWS_REGION"
    echo ""
    
    # Get outputs from Terraform
    cd "$TERRAFORM_DIR"
    
    echo "=== Resources Created ==="
    
    # DynamoDB tables
    DYNAMODB_TABLES=$(terraform output -json dynamodb_tables 2>/dev/null || echo "{}")
    if [[ "$DYNAMODB_TABLES" != "{}" ]]; then
        echo "DynamoDB Tables:"
        echo "$DYNAMODB_TABLES" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # SQS queues
    SQS_QUEUES=$(terraform output -json sqs_queues 2>/dev/null || echo "{}")
    if [[ "$SQS_QUEUES" != "{}" ]]; then
        echo "SQS Queues:"
        echo "$SQS_QUEUES" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # SNS topics
    SNS_TOPICS=$(terraform output -json sns_topics 2>/dev/null || echo "{}")
    if [[ "$SNS_TOPICS" != "{}" ]]; then
        echo "SNS Topics:"
        echo "$SNS_TOPICS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # Lambda functions
    LAMBDA_FUNCTIONS=$(terraform output -json lambda_functions 2>/dev/null || echo "{}")
    if [[ "$LAMBDA_FUNCTIONS" != "{}" ]]; then
        echo "Lambda Functions:"
        echo "$LAMBDA_FUNCTIONS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # Step Functions
    STEPFUNCTIONS=$(terraform output -json stepfunctions_state_machines 2>/dev/null || echo "{}")
    if [[ "$STEPFUNCTIONS" != "{}" ]]; then
        echo "Step Functions:"
        echo "$STEPFUNCTIONS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name)"'
    fi
    
    # API Gateway
    API_GATEWAY=$(terraform output -json api_gateway 2>/dev/null || echo "{}")
    if [[ "$API_GATEWAY" != "{}" ]]; then
        echo "API Gateway:"
        echo "  - URL: $(echo "$API_GATEWAY" | jq -r '.endpoint // "N/A"')"
    fi
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Test the API endpoints"
    echo "2. Configure monitoring and alerting"
    echo "3. Set up CI/CD pipelines"
    echo "4. Review security settings"
    echo "5. Configure backup and disaster recovery"
    echo ""
    echo "=== Important URLs ==="
    echo "AWS Console: https://console.aws.amazon.com/"
    echo "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups"
    echo "Lambda Console: https://console.aws.amazon.com/lambda/home?region=$AWS_REGION"
    echo "DynamoDB Console: https://console.aws.amazon.com/dynamodb/home?region=$AWS_REGION"
    echo "Step Functions Console: https://console.aws.amazon.com/states/home?region=$AWS_REGION"
    echo "API Gateway Console: https://console.aws.amazon.com/apigateway/home?region=$AWS_REGION"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary Lambda packages
    rm -rf temp_lambda_packages
    rm -f order_processor.zip notification_sender.zip
    
    # Remove Terraform plan file
    cd "$TERRAFORM_DIR"
    rm -f tfplan
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Serverless Platform Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    validate_configuration
    install_python_dependencies
    create_lambda_packages
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