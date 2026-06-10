#!/bin/bash

# AWS Data & Analytics Platform Deployment Script
# This script deploys the complete data analytics platform using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
PYTHON_DIR="$PROJECT_ROOT/python"

# Default values
AWS_REGION="us-east-1"
PROJECT_NAME="aws-data-analytics"
ENVIRONMENT="production"
DATA_LAKE_BUCKET_NAME=""
VPC_ID=""
REDSHIFT_SUBNET_IDS=""
REDSHIFT_MASTER_PASSWORD=""
CREATE_SAGEMAKER_NOTEBOOK="true"
DEPLOY_METHOD="terraform"

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

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy AWS Data & Analytics Platform

OPTIONS:
    -r, --region REGION              AWS region (default: us-east-1)
    -p, --project-name NAME          Project name (default: aws-data-analytics)
    -e, --environment ENV            Environment (default: production)
    -b, --bucket-name NAME           S3 bucket name for data lake (required)
    -v, --vpc-id ID                  VPC ID (required)
    -s, --subnet-ids IDS             Comma-separated subnet IDs for Redshift (required)
    -w, --password PASSWORD          Redshift master password (required)
    -n, --no-sagemaker              Skip SageMaker notebook creation
    -m, --method METHOD              Deployment method: terraform (default)
    -h, --help                       Show this help message

EXAMPLES:
    # Deploy with all required parameters
    $0 --bucket-name my-data-lake-bucket --vpc-id vpc-12345678 --subnet-ids subnet-12345678,subnet-87654321 --password MySecurePassword123

    # Deploy without SageMaker notebook
    $0 --bucket-name my-data-lake-bucket --vpc-id vpc-12345678 --subnet-ids subnet-12345678,subnet-87654321 --password MySecurePassword123 --no-sagemaker

    # Deploy to different region
    $0 --region us-west-2 --bucket-name my-data-lake-bucket --vpc-id vpc-12345678 --subnet-ids subnet-12345678,subnet-87654321 --password MySecurePassword123
EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to validate parameters
validate_parameters() {
    print_status "Validating parameters..."
    
    if [ -z "$DATA_LAKE_BUCKET_NAME" ]; then
        print_error "S3 bucket name is required. Use --bucket-name option."
        exit 1
    fi
    
    if [ -z "$VPC_ID" ]; then
        print_error "VPC ID is required. Use --vpc-id option."
        exit 1
    fi
    
    if [ -z "$REDSHIFT_SUBNET_IDS" ]; then
        print_error "Redshift subnet IDs are required. Use --subnet-ids option."
        exit 1
    fi
    
    if [ -z "$REDSHIFT_MASTER_PASSWORD" ]; then
        print_error "Redshift master password is required. Use --password option."
        exit 1
    fi
    
    # Validate password strength
    if [ ${#REDSHIFT_MASTER_PASSWORD} -lt 8 ]; then
        print_error "Redshift master password must be at least 8 characters long."
        exit 1
    fi
    
    print_success "Parameters validated"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "$PYTHON_DIR/requirements.txt" ]; then
        pip3 install -r "$PYTHON_DIR/requirements.txt"
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping Python dependency installation"
    fi
}

# Function to deploy with Terraform
deploy_with_terraform() {
    print_status "Deploying with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Create terraform.tfvars file
    print_status "Creating terraform.tfvars..."
    cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
project_name = "$PROJECT_NAME"
environment = "$ENVIRONMENT"
data_lake_bucket_name = "$DATA_LAKE_BUCKET_NAME"
vpc_id = "$VPC_ID"
redshift_subnet_ids = ["$(echo $REDSHIFT_SUBNET_IDS | tr ',' '", "')"]
redshift_master_password = "$REDSHIFT_MASTER_PASSWORD"
create_sagemaker_notebook = $CREATE_SAGEMAKER_NOTEBOOK
EOF
    
    # Plan Terraform deployment
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply Terraform deployment
    print_status "Applying Terraform deployment..."
    terraform apply tfplan
    
    print_success "Terraform deployment completed"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test S3 bucket access
    if aws s3 ls "s3://$DATA_LAKE_BUCKET_NAME" &> /dev/null; then
        print_success "S3 bucket access test passed"
    else
        print_warning "S3 bucket access test failed"
    fi
    
    # Test Kinesis stream
    if aws kinesis describe-stream --stream-name "${PROJECT_NAME}-data-stream" --region "$AWS_REGION" &> /dev/null; then
        print_success "Kinesis stream test passed"
    else
        print_warning "Kinesis stream test failed"
    fi
    
    # Test Redshift cluster
    if aws redshift describe-clusters --cluster-identifier "${PROJECT_NAME}-cluster" --region "$AWS_REGION" &> /dev/null; then
        print_success "Redshift cluster test passed"
    else
        print_warning "Redshift cluster test failed"
    fi
}

# Function to show deployment summary
show_deployment_summary() {
    print_status "Deployment Summary"
    echo "=================="
    echo "Project Name: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "AWS Region: $AWS_REGION"
    echo "Data Lake Bucket: $DATA_LAKE_BUCKET_NAME"
    echo "VPC ID: $VPC_ID"
    echo "SageMaker Notebook: $CREATE_SAGEMAKER_NOTEBOOK"
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your data sources to write to the Kinesis stream"
    echo "2. Set up data processing jobs in Glue"
    echo "3. Connect your analytics tools to Redshift"
    echo "4. Start using SageMaker for machine learning (if enabled)"
}

# Function to cleanup on failure
cleanup_on_failure() {
    print_error "Deployment failed. Cleaning up..."
    
    if [ -d "$TERRAFORM_DIR" ]; then
        cd "$TERRAFORM_DIR"
        if [ -f "terraform.tfstate" ]; then
            print_status "Destroying Terraform resources..."
            terraform destroy -auto-approve
        fi
    fi
    
    print_warning "Cleanup completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--bucket-name)
            DATA_LAKE_BUCKET_NAME="$2"
            shift 2
            ;;
        -v|--vpc-id)
            VPC_ID="$2"
            shift 2
            ;;
        -s|--subnet-ids)
            REDSHIFT_SUBNET_IDS="$2"
            shift 2
            ;;
        -w|--password)
            REDSHIFT_MASTER_PASSWORD="$2"
            shift 2
            ;;
        -n|--no-sagemaker)
            CREATE_SAGEMAKER_NOTEBOOK="false"
            shift
            ;;
        -m|--method)
            DEPLOY_METHOD="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting AWS Data & Analytics Platform deployment..."
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    # Check prerequisites
    check_prerequisites
    
    # Validate parameters
    validate_parameters
    
    # Install Python dependencies
    install_python_dependencies
    
    # Deploy based on method
    case $DEPLOY_METHOD in
        terraform)
            deploy_with_terraform
            ;;
        *)
            print_error "Unsupported deployment method: $DEPLOY_METHOD"
            exit 1
            ;;
    esac
    
    # Test deployment
    test_deployment
    
    # Show deployment summary
    show_deployment_summary
    
    print_success "AWS Data & Analytics Platform deployment completed successfully!"
}

# Run main function
main "$@"