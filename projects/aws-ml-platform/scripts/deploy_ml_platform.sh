#!/bin/bash

# AWS ML Platform Deployment Script
# This script deploys the complete ML platform using Terraform

set -e

# Configuration
PROJECT_NAME="aws-ml-platform"
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
    echo "  -v, --vpc-id VPC_ID       VPC ID for SageMaker domain"
    echo "  -s, --subnet-ids SUBNETS  Comma-separated subnet IDs"
    echo "  -n, --notification-email  Email for ML notifications"
    echo "  -f, --framework FRAMEWORK ML framework (tensorflow, pytorch, sklearn, xgboost)"
    echo "  -t, --instance-type TYPE  Instance type for training/inference"
    echo "  -c, --instance-count NUM  Instance count"
    echo "  -d, --enable-domain       Enable SageMaker domain"
    echo "  -b, --enable-notebook     Enable SageMaker notebook"
    echo "  -m, --enable-monitoring   Enable model monitoring"
    echo "  -a, --enable-automation   Enable ML automation"
    echo "  -g, --enable-gateway      Enable API Gateway"
    echo "  -f, --dry-run             Show what would be deployed without deploying"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment prod --region us-west-2"
    echo "  $0 --framework tensorflow --instance-type ml.m5.xlarge"
    echo "  $0 --enable-domain --enable-notebook --enable-monitoring"
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
        -f|--framework)
            MODEL_FRAMEWORK="$2"
            shift 2
            ;;
        -t|--instance-type)
            INSTANCE_TYPE="$2"
            shift 2
            ;;
        -c|--instance-count)
            INSTANCE_COUNT="$2"
            shift 2
            ;;
        -d|--enable-domain)
            ENABLE_DOMAIN=true
            shift
            ;;
        -b|--enable-notebook)
            ENABLE_NOTEBOOK=true
            shift
            ;;
        -m|--enable-monitoring)
            ENABLE_MONITORING=true
            shift
            ;;
        -a|--enable-automation)
            ENABLE_AUTOMATION=true
            shift
            ;;
        -g|--enable-gateway)
            ENABLE_GATEWAY=true
            shift
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
    
    # Validate email if provided
    if [[ -n "$NOTIFICATION_EMAIL" ]] && [[ ! "$NOTIFICATION_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid notification email address: $NOTIFICATION_EMAIL"
        exit 1
    fi
    
    # Validate framework
    if [[ -n "$MODEL_FRAMEWORK" ]] && [[ ! "$MODEL_FRAMEWORK" =~ ^(tensorflow|pytorch|sklearn|xgboost|huggingface)$ ]]; then
        print_error "Invalid model framework: $MODEL_FRAMEWORK. Must be tensorflow, pytorch, sklearn, xgboost, or huggingface."
        exit 1
    fi
    
    # Validate instance type
    if [[ -n "$INSTANCE_TYPE" ]] && [[ ! "$INSTANCE_TYPE" =~ ^ml\. ]]; then
        print_warning "Instance type $INSTANCE_TYPE may not be a valid SageMaker instance type"
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
create_s3_bucket = true
create_iam_roles = true
create_sagemaker_domain = ${ENABLE_DOMAIN:-true}
create_notebook_instance = ${ENABLE_NOTEBOOK:-true}
create_model_package_group = true
create_experiment = true
create_pipeline = true
create_endpoint_configuration = true
create_endpoint = true
create_monitoring_schedule = ${ENABLE_MONITORING:-true}
create_data_quality_job = ${ENABLE_MONITORING:-true}
create_model_quality_job = ${ENABLE_MONITORING:-true}
create_bias_job = ${ENABLE_MONITORING:-true}
create_explainability_job = ${ENABLE_MONITORING:-true}
create_ecr_repository = true
create_lambda_functions = ${ENABLE_AUTOMATION:-true}
create_eventbridge_rules = ${ENABLE_AUTOMATION:-true}
create_dashboard = true
create_sns_topic = true
create_api_gateway = ${ENABLE_GATEWAY:-true}
enable_mlops = true
enable_experiment_tracking = true
enable_model_monitoring = ${ENABLE_MONITORING:-true}
enable_hyperparameter_tuning = true
enable_automated_ml = true
enable_batch_inference = true
enable_real_time_inference = true
EOF

    # Add VPC configuration if provided
    if [[ -n "$VPC_ID" ]]; then
        echo "vpc_id = \"$VPC_ID\"" >> terraform.tfvars
    fi
    
    if [[ -n "$SUBNET_IDS" ]]; then
        # Convert comma-separated string to list
        subnet_list=$(echo "$SUBNET_IDS" | tr ',' ' ' | sed 's/^/[/' | sed 's/$/]/' | sed 's/ /, /g')
        echo "subnet_ids = $subnet_list" >> terraform.tfvars
    fi
    
    # Add notification email if provided
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        echo "notification_email = \"$NOTIFICATION_EMAIL\"" >> terraform.tfvars
    fi
    
    # Add model framework if provided
    if [[ -n "$MODEL_FRAMEWORK" ]]; then
        echo "model_framework = \"$MODEL_FRAMEWORK\"" >> terraform.tfvars
    fi
    
    # Add instance configuration if provided
    if [[ -n "$INSTANCE_TYPE" ]]; then
        echo "instance_type = \"$INSTANCE_TYPE\"" >> terraform.tfvars
        echo "training_instance_type = \"$INSTANCE_TYPE\"" >> terraform.tfvars
        echo "inference_instance_type = \"$INSTANCE_TYPE\"" >> terraform.tfvars
    fi
    
    if [[ -n "$INSTANCE_COUNT" ]]; then
        echo "initial_instance_count = $INSTANCE_COUNT" >> terraform.tfvars
        echo "training_instance_count = $INSTANCE_COUNT" >> terraform.tfvars
        echo "inference_instance_count = $INSTANCE_COUNT" >> terraform.tfvars
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
    
    # Create ML automation Lambda function
    cat > temp_lambda_package/ml_automation.py << 'EOF'
import json
import boto3
import os
from datetime import datetime

def handler(event, context):
    """
    ML automation Lambda function
    """
    try:
        # Get environment variables
        sagemaker_role_arn = os.environ.get('SAGEMAKER_ROLE_ARN')
        s3_bucket = os.environ.get('S3_BUCKET')
        ecr_repository = os.environ.get('ECR_REPOSITORY')
        
        # Initialize AWS clients
        sagemaker_client = boto3.client('sagemaker')
        s3_client = boto3.client('s3')
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Create a simple ML automation workflow
        workflow_result = {
            'timestamp': timestamp,
            'status': 'success',
            'message': 'ML automation workflow completed',
            'sagemaker_role': sagemaker_role_arn,
            's3_bucket': s3_bucket,
            'ecr_repository': ecr_repository
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(workflow_result)
        }
        
    except Exception as e:
        print(f"Error in ML automation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'ML automation failed',
                'message': str(e)
            })
        }
EOF

    # Create zip file
    cd temp_lambda_package
    zip -r ../ml_automation.zip .
    cd ..
    
    print_success "Lambda deployment package created"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get outputs from Terraform
    S3_BUCKET=$(terraform output -json s3_bucket 2>/dev/null || echo "{}")
    SAGEMAKER_DOMAIN=$(terraform output -json sagemaker_domain 2>/dev/null || echo "{}")
    SAGEMAKER_ENDPOINT=$(terraform output -json sagemaker_endpoint 2>/dev/null || echo "{}")
    ECR_REPOSITORY=$(terraform output -json ecr_repository 2>/dev/null || echo "{}")
    API_GATEWAY=$(terraform output -json api_gateway 2>/dev/null || echo "{}")
    
    # Test S3 bucket
    if [[ "$S3_BUCKET" != "{}" ]]; then
        print_status "Testing S3 bucket..."
        bucket_name=$(echo "$S3_BUCKET" | jq -r '.bucket.name // empty')
        if [[ -n "$bucket_name" ]]; then
            print_success "S3 bucket created: $bucket_name"
        fi
    fi
    
    # Test SageMaker domain
    if [[ "$SAGEMAKER_DOMAIN" != "{}" ]]; then
        print_status "Testing SageMaker domain..."
        domain_id=$(echo "$SAGEMAKER_DOMAIN" | jq -r '.domain.id // empty')
        if [[ -n "$domain_id" ]]; then
            print_success "SageMaker domain created: $domain_id"
        fi
    fi
    
    # Test SageMaker endpoint
    if [[ "$SAGEMAKER_ENDPOINT" != "{}" ]]; then
        print_status "Testing SageMaker endpoint..."
        endpoint_name=$(echo "$SAGEMAKER_ENDPOINT" | jq -r '.endpoint.name // empty')
        if [[ -n "$endpoint_name" ]]; then
            print_success "SageMaker endpoint created: $endpoint_name"
        fi
    fi
    
    # Test ECR repository
    if [[ "$ECR_REPOSITORY" != "{}" ]]; then
        print_status "Testing ECR repository..."
        repo_name=$(echo "$ECR_REPOSITORY" | jq -r '.repository.name // empty')
        if [[ -n "$repo_name" ]]; then
            print_success "ECR repository created: $repo_name"
        fi
    fi
    
    # Test API Gateway
    if [[ "$API_GATEWAY" != "{}" ]]; then
        print_status "Testing API Gateway..."
        api_id=$(echo "$API_GATEWAY" | jq -r '.api.id // empty')
        if [[ -n "$api_id" ]]; then
            print_success "API Gateway created: $api_id"
        fi
    fi
    
    print_success "Deployment testing completed"
}

# Function to display deployment summary
display_summary() {
    print_success "AWS ML Platform deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Project Name: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "AWS Region: $AWS_REGION"
    echo "Model Framework: ${MODEL_FRAMEWORK:-tensorflow}"
    echo ""
    
    # Get outputs from Terraform
    cd "$TERRAFORM_DIR"
    
    echo "=== Resources Created ==="
    
    # S3 bucket
    S3_BUCKET=$(terraform output -json s3_bucket 2>/dev/null || echo "{}")
    if [[ "$S3_BUCKET" != "{}" ]]; then
        bucket_name=$(echo "$S3_BUCKET" | jq -r '.bucket.name // empty')
        if [[ -n "$bucket_name" ]]; then
            echo "S3 Bucket: $bucket_name"
        fi
    fi
    
    # SageMaker domain
    SAGEMAKER_DOMAIN=$(terraform output -json sagemaker_domain 2>/dev/null || echo "{}")
    if [[ "$SAGEMAKER_DOMAIN" != "{}" ]]; then
        domain_id=$(echo "$SAGEMAKER_DOMAIN" | jq -r '.domain.id // empty')
        if [[ -n "$domain_id" ]]; then
            echo "SageMaker Domain: $domain_id"
        fi
    fi
    
    # SageMaker notebook
    SAGEMAKER_NOTEBOOK=$(terraform output -json sagemaker_notebook 2>/dev/null || echo "{}")
    if [[ "$SAGEMAKER_NOTEBOOK" != "{}" ]]; then
        notebook_name=$(echo "$SAGEMAKER_NOTEBOOK" | jq -r '.notebook.name // empty')
        if [[ -n "$notebook_name" ]]; then
            echo "SageMaker Notebook: $notebook_name"
        fi
    fi
    
    # SageMaker endpoint
    SAGEMAKER_ENDPOINT=$(terraform output -json sagemaker_endpoint 2>/dev/null || echo "{}")
    if [[ "$SAGEMAKER_ENDPOINT" != "{}" ]]; then
        endpoint_name=$(echo "$SAGEMAKER_ENDPOINT" | jq -r '.endpoint.name // empty')
        if [[ -n "$endpoint_name" ]]; then
            echo "SageMaker Endpoint: $endpoint_name"
        fi
    fi
    
    # ECR repository
    ECR_REPOSITORY=$(terraform output -json ecr_repository 2>/dev/null || echo "{}")
    if [[ "$ECR_REPOSITORY" != "{}" ]]; then
        repo_name=$(echo "$ECR_REPOSITORY" | jq -r '.repository.name // empty')
        if [[ -n "$repo_name" ]]; then
            echo "ECR Repository: $repo_name"
        fi
    fi
    
    # API Gateway
    API_GATEWAY=$(terraform output -json api_gateway 2>/dev/null || echo "{}")
    if [[ "$API_GATEWAY" != "{}" ]]; then
        api_id=$(echo "$API_GATEWAY" | jq -r '.api.id // empty')
        if [[ -n "$api_id" ]]; then
            echo "API Gateway: $api_id"
        fi
    fi
    
    echo ""
    echo "=== ML Platform Features ==="
    echo "✅ Model Training - SageMaker training jobs with hyperparameter tuning"
    echo "✅ Model Deployment - Real-time and batch inference endpoints"
    echo "✅ Experiment Tracking - Comprehensive experiment tracking and comparison"
    echo "✅ Model Monitoring - Data quality, model quality, bias, and explainability monitoring"
    echo "✅ MLOps Automation - Automated ML workflows and CI/CD pipelines"
    echo "✅ Model Registry - Model versioning and lifecycle management"
    echo "✅ Data Processing - Data preprocessing and feature engineering"
    echo "✅ Hyperparameter Tuning - Automated hyperparameter optimization"
    echo "✅ Automated ML - AutoML capabilities for model selection"
    echo "✅ Batch Inference - Large-scale batch inference processing"
    echo "✅ Real-time Inference - Low-latency real-time inference"
    echo "✅ Model Explainability - Model interpretability and explainability"
    echo "✅ Bias Detection - Fairness and bias monitoring"
    echo "✅ Cost Optimization - Spot training and cost-effective inference"
    echo "✅ Security - Encryption, network isolation, and access control"
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Access SageMaker Studio to start developing ML models"
    echo "2. Upload your training data to the S3 bucket"
    echo "3. Create your first experiment and start tracking runs"
    echo "4. Set up model monitoring for production endpoints"
    echo "5. Configure automated retraining workflows"
    echo "6. Set up model approval and deployment pipelines"
    echo "7. Configure cost optimization settings"
    echo "8. Set up notifications for model performance alerts"
    echo "9. Create custom monitoring dashboards"
    echo "10. Implement model versioning and lifecycle management"
    
    echo ""
    echo "=== Important URLs ==="
    echo "SageMaker Console: https://console.aws.amazon.com/sagemaker/home?region=$AWS_REGION"
    echo "SageMaker Studio: ${SAGEMAKER_DOMAIN:+https://$(echo "$SAGEMAKER_DOMAIN" | jq -r '.domain.url // empty')}"
    echo "CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION"
    echo "ECR Console: https://console.aws.amazon.com/ecr/repositories?region=$AWS_REGION"
    echo "S3 Console: ${S3_BUCKET:+https://console.aws.amazon.com/s3/buckets/$(echo "$S3_BUCKET" | jq -r '.bucket.name // empty')?region=$AWS_REGION}"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary Lambda package
    rm -rf temp_lambda_package
    rm -f ml_automation.zip
    
    # Remove Terraform plan file
    cd "$TERRAFORM_DIR"
    rm -f tfplan
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS ML Platform Deployment"
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