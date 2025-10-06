#!/bin/bash

# AWS CI/CD & DevOps Platform Deployment Script
# This script deploys the complete CI/CD platform using either Terraform or CloudFormation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEPLOYMENT_METHOD="terraform"
AWS_REGION="us-east-1"
PROJECT_NAME="aws-cicd-devops"
ENVIRONMENT="production"
STACK_NAME=""
SOURCE_PROVIDER="CodeCommit"
SOURCE_REPOSITORY=""
SOURCE_BRANCH="main"
GITHUB_OWNER=""
GITHUB_REPO=""
GITHUB_TOKEN=""
CREATE_TEST_PROJECT="true"
CREATE_CODEDEPLOY_APP="true"
CREATE_PIPELINE="true"
CREATE_ALARMS="true"

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

Deploy AWS CI/CD & DevOps Platform

OPTIONS:
    -m, --method METHOD          Deployment method (terraform|cloudformation) [default: terraform]
    -r, --region REGION          AWS region [default: us-east-1]
    -p, --project-name NAME      Project name [default: aws-cicd-devops]
    -e, --environment ENV        Environment [default: production]
    -s, --stack-name NAME        CloudFormation stack name [default: PROJECT_NAME-ENVIRONMENT]
    --source-provider PROVIDER   Source provider (CodeCommit|GitHub|S3) [default: CodeCommit]
    --source-repo REPO           Source repository name
    --source-branch BRANCH       Source branch [default: main]
    --github-owner OWNER         GitHub repository owner
    --github-repo REPO           GitHub repository name
    --github-token TOKEN         GitHub OAuth token
    --no-test                    Don't create test project
    --no-codedeploy              Don't create CodeDeploy application
    --no-pipeline                Don't create CodePipeline
    --no-alarms                  Don't create CloudWatch alarms
    -h, --help                   Show this help message

EXAMPLES:
    # Deploy with Terraform (default)
    $0 --source-repo my-app-repo

    # Deploy with CloudFormation
    $0 --method cloudformation --source-repo my-app-repo

    # Deploy with GitHub source
    $0 --source-provider GitHub --github-owner myorg --github-repo my-app --github-token token123

    # Deploy without test project
    $0 --source-repo my-app-repo --no-test

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
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check deployment method specific prerequisites
    if [ "$DEPLOYMENT_METHOD" = "terraform" ]; then
        if ! command -v terraform &> /dev/null; then
            print_error "Terraform is not installed. Please install it first."
            exit 1
        fi
    elif [ "$DEPLOYMENT_METHOD" = "cloudformation" ]; then
        if ! command -v aws cloudformation &> /dev/null; then
            print_error "AWS CloudFormation CLI is not available."
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Function to validate parameters
validate_parameters() {
    print_status "Validating parameters..."
    
    # Validate deployment method
    if [[ ! "$DEPLOYMENT_METHOD" =~ ^(terraform|cloudformation)$ ]]; then
        print_error "Invalid deployment method: $DEPLOYMENT_METHOD. Must be 'terraform' or 'cloudformation'"
        exit 1
    fi
    
    # Validate source provider
    if [[ ! "$SOURCE_PROVIDER" =~ ^(CodeCommit|GitHub|S3)$ ]]; then
        print_error "Invalid source provider: $SOURCE_PROVIDER. Must be 'CodeCommit', 'GitHub', or 'S3'"
        exit 1
    fi
    
    # Validate required parameters based on source provider
    if [ "$SOURCE_PROVIDER" = "CodeCommit" ] && [ -z "$SOURCE_REPOSITORY" ]; then
        print_error "Source repository is required for CodeCommit"
        exit 1
    fi
    
    if [ "$SOURCE_PROVIDER" = "GitHub" ]; then
        if [ -z "$GITHUB_OWNER" ] || [ -z "$GITHUB_REPO" ] || [ -z "$GITHUB_TOKEN" ]; then
            print_error "GitHub owner, repo, and token are required for GitHub source"
            exit 1
        fi
    fi
    
    # Set default stack name if not provided
    if [ -z "$STACK_NAME" ]; then
        STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
    fi
    
    print_success "Parameters validation passed"
}

# Function to deploy with Terraform
deploy_terraform() {
    print_status "Deploying with Terraform..."
    
    cd terraform
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Create terraform.tfvars file
    print_status "Creating terraform.tfvars file..."
    cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
project_name = "$PROJECT_NAME"
environment = "$ENVIRONMENT"
source_provider = "$SOURCE_PROVIDER"
source_repository = "$SOURCE_REPOSITORY"
source_branch = "$SOURCE_BRANCH"
github_owner = "$GITHUB_OWNER"
github_repo = "$GITHUB_REPO"
github_token = "$GITHUB_TOKEN"
create_test_project = $CREATE_TEST_PROJECT
create_codedeploy_app = $CREATE_CODEDEPLOY_APP
create_pipeline = $CREATE_PIPELINE
create_alarms = $CREATE_ALARMS
EOF
    
    # Plan deployment
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply deployment
    print_status "Applying Terraform deployment..."
    terraform apply tfplan
    
    print_success "Terraform deployment completed"
    
    # Show outputs
    print_status "Terraform outputs:"
    terraform output
    
    cd ..
}

# Function to deploy with CloudFormation
deploy_cloudformation() {
    print_status "Deploying with CloudFormation..."
    
    # Prepare parameters
    PARAMETERS="ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME"
    PARAMETERS="$PARAMETERS ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    PARAMETERS="$PARAMETERS ParameterKey=SourceProvider,ParameterValue=$SOURCE_PROVIDER"
    PARAMETERS="$PARAMETERS ParameterKey=SourceRepository,ParameterValue=$SOURCE_REPOSITORY"
    PARAMETERS="$PARAMETERS ParameterKey=SourceBranch,ParameterValue=$SOURCE_BRANCH"
    PARAMETERS="$PARAMETERS ParameterKey=GitHubOwner,ParameterValue=$GITHUB_OWNER"
    PARAMETERS="$PARAMETERS ParameterKey=GitHubRepo,ParameterValue=$GITHUB_REPO"
    PARAMETERS="$PARAMETERS ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN"
    PARAMETERS="$PARAMETERS ParameterKey=CreateTestProject,ParameterValue=$CREATE_TEST_PROJECT"
    PARAMETERS="$PARAMETERS ParameterKey=CreateCodeDeployApp,ParameterValue=$CREATE_CODEDEPLOY_APP"
    PARAMETERS="$PARAMETERS ParameterKey=CreatePipeline,ParameterValue=$CREATE_PIPELINE"
    PARAMETERS="$PARAMETERS ParameterKey=CreateAlarms,ParameterValue=$CREATE_ALARMS"
    
    # Deploy stack
    print_status "Deploying CloudFormation stack: $STACK_NAME"
    aws cloudformation deploy \
        --template-file cloudformation/cicd-platform.yaml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides $PARAMETERS \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION"
    
    print_success "CloudFormation deployment completed"
    
    # Show outputs
    print_status "CloudFormation outputs:"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
}

# Function to cleanup resources
cleanup() {
    print_status "Cleaning up resources..."
    
    if [ "$DEPLOYMENT_METHOD" = "terraform" ]; then
        cd terraform
        terraform destroy -auto-approve
        cd ..
    elif [ "$DEPLOYMENT_METHOD" = "cloudformation" ]; then
        aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$AWS_REGION"
        print_status "Stack deletion initiated. Check AWS Console for status."
    fi
    
    print_success "Cleanup completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--method)
            DEPLOYMENT_METHOD="$2"
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
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        --source-provider)
            SOURCE_PROVIDER="$2"
            shift 2
            ;;
        --source-repo)
            SOURCE_REPOSITORY="$2"
            shift 2
            ;;
        --source-branch)
            SOURCE_BRANCH="$2"
            shift 2
            ;;
        --github-owner)
            GITHUB_OWNER="$2"
            shift 2
            ;;
        --github-repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        --github-token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        --no-test)
            CREATE_TEST_PROJECT="false"
            shift
            ;;
        --no-codedeploy)
            CREATE_CODEDEPLOY_APP="false"
            shift
            ;;
        --no-pipeline)
            CREATE_PIPELINE="false"
            shift
            ;;
        --no-alarms)
            CREATE_ALARMS="false"
            shift
            ;;
        --cleanup)
            cleanup
            exit 0
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
    print_status "Starting AWS CI/CD & DevOps Platform deployment..."
    print_status "Deployment method: $DEPLOYMENT_METHOD"
    print_status "AWS region: $AWS_REGION"
    print_status "Project name: $PROJECT_NAME"
    print_status "Environment: $ENVIRONMENT"
    
    check_prerequisites
    validate_parameters
    
    if [ "$DEPLOYMENT_METHOD" = "terraform" ]; then
        deploy_terraform
    elif [ "$DEPLOYMENT_METHOD" = "cloudformation" ]; then
        deploy_cloudformation
    fi
    
    print_success "AWS CI/CD & DevOps Platform deployment completed successfully!"
    print_status "You can now use the deployed CI/CD platform for your applications."
}

# Run main function
main "$@"