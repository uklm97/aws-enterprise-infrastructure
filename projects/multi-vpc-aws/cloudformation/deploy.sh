#!/bin/bash

# Multi-VPC AWS Environment CloudFormation Deployment Script
# This script deploys the complete multi-VPC environment using CloudFormation

set -e

# Configuration
STACK_NAME="multi-vpc-environment"
REGION="us-west-2"
ENVIRONMENT="multi-vpc"
PROJECT_NAME="multi-vpc-demo"

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

# Function to check if AWS CLI is installed and configured
check_aws_cli() {
    print_status "Checking AWS CLI installation..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is installed and configured"
}

# Function to validate CloudFormation templates
validate_templates() {
    print_status "Validating CloudFormation templates..."
    
    for template in *.json; do
        if [ -f "$template" ]; then
            print_status "Validating $template..."
            if aws cloudformation validate-template --template-body file://$template --region $REGION &> /dev/null; then
                print_success "$template is valid"
            else
                print_error "$template is invalid"
                exit 1
            fi
        fi
    done
}

# Function to deploy main VPC stack
deploy_vpc_stack() {
    print_status "Deploying VPC stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME-vpc \
        --template-body file://main.json \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "Waiting for VPC stack to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME-vpc \
        --region $REGION
    
    print_success "VPC stack deployed successfully"
}

# Function to deploy networking stack
deploy_networking_stack() {
    print_status "Deploying networking stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME-networking \
        --template-body file://networking.json \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
            ParameterKey=EnableNATGateway,ParameterValue=true \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "Waiting for networking stack to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME-networking \
        --region $REGION
    
    print_success "Networking stack deployed successfully"
}

# Function to deploy security stack
deploy_security_stack() {
    print_status "Deploying security stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME-security \
        --template-body file://security.json \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "Waiting for security stack to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME-security \
        --region $REGION
    
    print_success "Security stack deployed successfully"
}

# Function to deploy compute stack
deploy_compute_stack() {
    print_status "Deploying compute stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME-compute \
        --template-body file://compute.json \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
            ParameterKey=InstanceType,ParameterValue=t3.micro \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "Waiting for compute stack to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME-compute \
        --region $REGION
    
    print_success "Compute stack deployed successfully"
}

# Function to deploy database stack
deploy_database_stack() {
    print_status "Deploying database stack..."
    
    aws cloudformation create-stack \
        --stack-name $STACK_NAME-database \
        --template-body file://database.json \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
            ParameterKey=DBInstanceClass,ParameterValue=db.t3.micro \
            ParameterKey=DBAllocatedStorage,ParameterValue=20 \
            ParameterKey=DBEngineVersion,ParameterValue=8.0.35 \
            ParameterKey=DBUsername,ParameterValue=admin \
            ParameterKey=DBPassword,ParameterValue=changeme123! \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "Waiting for database stack to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME-database \
        --region $REGION
    
    print_success "Database stack deployed successfully"
}

# Function to display stack outputs
display_outputs() {
    print_status "Displaying stack outputs..."
    
    echo ""
    echo "=== VPC Stack Outputs ==="
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME-vpc \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
    
    echo ""
    echo "=== Networking Stack Outputs ==="
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME-networking \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
    
    echo ""
    echo "=== Security Stack Outputs ==="
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME-security \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
}

# Function to clean up stacks
cleanup_stacks() {
    print_warning "This will delete all CloudFormation stacks. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Deleting stacks..."
        
        # Delete stacks in reverse order
        for stack in database compute security networking vpc; do
            if aws cloudformation describe-stacks --stack-name $STACK_NAME-$stack --region $REGION &> /dev/null; then
                print_status "Deleting $STACK_NAME-$stack..."
                aws cloudformation delete-stack --stack-name $STACK_NAME-$stack --region $REGION
                aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME-$stack --region $REGION
                print_success "$STACK_NAME-$stack deleted"
            fi
        done
        
        print_success "All stacks deleted successfully"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main deployment function
deploy_all() {
    print_status "Starting multi-VPC environment deployment..."
    
    check_aws_cli
    validate_templates
    
    deploy_vpc_stack
    deploy_networking_stack
    deploy_security_stack
    deploy_compute_stack
    deploy_database_stack
    
    display_outputs
    
    print_success "Multi-VPC environment deployed successfully!"
    print_status "You can now access your applications using the ALB URLs from the outputs above."
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy_all
        ;;
    "cleanup")
        cleanup_stacks
        ;;
    "validate")
        check_aws_cli
        validate_templates
        ;;
    "outputs")
        display_outputs
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|validate|outputs}"
        echo "  deploy   - Deploy the complete multi-VPC environment (default)"
        echo "  cleanup  - Delete all CloudFormation stacks"
        echo "  validate - Validate CloudFormation templates"
        echo "  outputs  - Display stack outputs"
        exit 1
        ;;
esac
