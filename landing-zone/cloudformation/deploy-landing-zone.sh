#!/bin/bash

# AWS Landing Zone CloudFormation Deployment Script
# This script automates the deployment of AWS Landing Zone using CloudFormation

set -e

# Configuration
REGION="us-east-1"
STACK_NAME="aws-landing-zone"
TEMPLATE_FILE="main.json"
PARAMETERS_FILE="parameters.json"

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
    echo "  -s, --stack-name NAME     CloudFormation stack name (default: aws-landing-zone)"
    echo "  -t, --template FILE       Template file (default: main.json)"
    echo "  -p, --parameters FILE     Parameters file (default: parameters.json)"
    echo "  -r, --region REGION       AWS region (default: us-east-1)"
    echo "  -c, --create              Create new stack"
    echo "  -u, --update              Update existing stack"
    echo "  -d, --delete              Delete stack"
    echo "  -v, --validate            Validate template only"
    echo "  -h, --help                Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -c                      # Create new landing zone"
    echo "  $0 -u                      # Update existing landing zone"
    echo "  $0 -d                      # Delete landing zone"
    echo "  $0 -v                      # Validate template"
    echo ""
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--stack-name)
                STACK_NAME="$2"
                shift 2
                ;;
            -t|--template)
                TEMPLATE_FILE="$2"
                shift 2
                ;;
            -p|--parameters)
                PARAMETERS_FILE="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -c|--create)
                ACTION="create"
                shift
                ;;
            -u|--update)
                ACTION="update"
                shift
                ;;
            -d|--delete)
                ACTION="delete"
                shift
                ;;
            -v|--validate)
                ACTION="validate"
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
}

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
    
    # Check if template file exists
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        print_error "Template file not found: $TEMPLATE_FILE"
        exit 1
    fi
    
    # Check if parameters file exists (if specified)
    if [[ -n "$PARAMETERS_FILE" && ! -f "$PARAMETERS_FILE" ]]; then
        print_error "Parameters file not found: $PARAMETERS_FILE"
        exit 1
    fi
    
    # Check if jq is installed (for JSON parsing)
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some features may not work properly."
    fi
    
    print_success "Prerequisites check completed"
}

# Function to validate template
validate_template() {
    print_status "Validating CloudFormation template..."
    
    if aws cloudformation validate-template --template-body file://"$TEMPLATE_FILE" --region "$REGION" &> /dev/null; then
        print_success "Template validation successful"
    else
        print_error "Template validation failed"
        exit 1
    fi
}

# Function to check if stack exists
check_stack_exists() {
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get stack status
get_stack_status() {
    aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "STACK_NOT_FOUND"
}

# Function to wait for stack operation
wait_for_stack_operation() {
    local operation=$1
    print_status "Waiting for stack $operation to complete..."
    
    while true; do
        STATUS=$(get_stack_status)
        
        case $STATUS in
            *"COMPLETE"*)
                if [[ $STATUS == *"ROLLBACK"* ]]; then
                    print_error "Stack $operation failed and rolled back"
                    exit 1
                else
                    print_success "Stack $operation completed successfully"
                    break
                fi
                ;;
            *"IN_PROGRESS"*)
                print_status "Stack $operation in progress: $STATUS. Waiting..."
                sleep 30
                ;;
            "STACK_NOT_FOUND")
                if [[ "$operation" == "deletion" ]]; then
                    print_success "Stack deletion completed"
                    break
                else
                    print_error "Stack not found"
                    exit 1
                fi
                ;;
            *)
                print_error "Unexpected stack status: $STATUS"
                exit 1
                ;;
        esac
    done
}

# Function to create parameters file if it doesn't exist
create_parameters_file() {
    if [[ ! -f "$PARAMETERS_FILE" ]]; then
        print_status "Creating parameters file: $PARAMETERS_FILE"
        
        cat > "$PARAMETERS_FILE" << EOF
[
  {
    "ParameterKey": "ProjectName",
    "ParameterValue": "aws-landing-zone"
  },
  {
    "ParameterKey": "Environment",
    "ParameterValue": "landing-zone"
  },
  {
    "ParameterKey": "AdminEmail",
    "ParameterValue": "admin@example.com"
  },
  {
    "ParameterKey": "OrganizationName",
    "ParameterValue": "My Organization"
  },
  {
    "ParameterKey": "EnableGuardDuty",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableSecurityHub",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableMacie",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableConfigRules",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "BudgetAmount",
    "ParameterValue": "1000"
  },
  {
    "ParameterKey": "BudgetThreshold",
    "ParameterValue": "80"
  },
  {
    "ParameterKey": "LogRetentionDays",
    "ParameterValue": "30"
  },
  {
    "ParameterKey": "SSOSessionDuration",
    "ParameterValue": "8"
  },
  {
    "ParameterKey": "EnableMultiRegionTrail",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableGlobalServiceEvents",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableS3DataEvents",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableCloudWatchLogs",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableSNSNotifications",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableBudgetAlerts",
    "ParameterValue": "true"
  }
]
EOF
        
        print_success "Parameters file created"
        print_warning "Please review and update the parameters file before deployment"
    fi
}

# Function to create stack
create_stack() {
    print_status "Creating CloudFormation stack: $STACK_NAME"
    
    if check_stack_exists; then
        print_error "Stack $STACK_NAME already exists. Use --update to update it or --delete to delete it first."
        exit 1
    fi
    
    # Create parameters file if it doesn't exist
    create_parameters_file
    
    # Create stack
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://"$TEMPLATE_FILE" \
        --parameters file://"$PARAMETERS_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --tags \
            Key=Project,Value=aws-landing-zone \
            Key=Environment,Value=landing-zone \
            Key=ManagedBy,Value=CloudFormation
    
    wait_for_stack_operation "creation"
}

# Function to update stack
update_stack() {
    print_status "Updating CloudFormation stack: $STACK_NAME"
    
    if ! check_stack_exists; then
        print_error "Stack $STACK_NAME does not exist. Use --create to create it."
        exit 1
    fi
    
    # Update stack
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://"$TEMPLATE_FILE" \
        --parameters file://"$PARAMETERS_FILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --tags \
            Key=Project,Value=aws-landing-zone \
            Key=Environment,Value=landing-zone \
            Key=ManagedBy,Value=CloudFormation
    
    wait_for_stack_operation "update"
}

# Function to delete stack
delete_stack() {
    print_status "Deleting CloudFormation stack: $STACK_NAME"
    
    if ! check_stack_exists; then
        print_error "Stack $STACK_NAME does not exist."
        exit 1
    fi
    
    # Confirm deletion
    read -p "Are you sure you want to delete stack $STACK_NAME? This action cannot be undone. (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stack deletion cancelled"
        exit 0
    fi
    
    # Delete stack
    aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
    
    wait_for_stack_operation "deletion"
}

# Function to display stack outputs
display_stack_outputs() {
    print_status "Retrieving stack outputs..."
    
    if check_stack_exists; then
        print_success "Stack outputs:"
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query "Stacks[0].Outputs" \
            --output table
    else
        print_warning "Stack does not exist, no outputs to display"
    fi
}

# Function to display stack resources
display_stack_resources() {
    print_status "Retrieving stack resources..."
    
    if check_stack_exists; then
        print_success "Stack resources:"
        aws cloudformation list-stack-resources \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query "StackResourceSummaries[].{LogicalId:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}" \
            --output table
    else
        print_warning "Stack does not exist, no resources to display"
    fi
}

# Function to display stack events
display_stack_events() {
    print_status "Retrieving recent stack events..."
    
    if check_stack_exists; then
        print_success "Recent stack events:"
        aws cloudformation describe-stack-events \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query "StackEvents[0:10].{Timestamp:Timestamp,LogicalId:LogicalResourceId,Status:ResourceStatus,Reason:ResourceStatusReason}" \
            --output table
    else
        print_warning "Stack does not exist, no events to display"
    fi
}

# Function to display deployment summary
display_deployment_summary() {
    print_success "AWS Landing Zone deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Stack Name: $STACK_NAME"
    echo "Region: $REGION"
    echo "Template: $TEMPLATE_FILE"
    echo "Parameters: $PARAMETERS_FILE"
    echo ""
    
    # Display outputs
    display_stack_outputs
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Access AWS Organizations console to view the organization structure"
    echo "2. Configure AWS SSO for user access"
    echo "3. Create additional accounts using the account provisioning script"
    echo "4. Configure custom guardrails and policies"
    echo "5. Set up monitoring and alerting"
    echo ""
    echo "=== Important URLs ==="
    echo "CloudFormation Console: https://console.aws.amazon.com/cloudformation"
    echo "AWS Organizations: https://console.aws.amazon.com/organizations"
    echo "AWS SSO Console: https://console.aws.amazon.com/singlesignon"
    echo "CloudWatch Dashboards: https://console.aws.amazon.com/cloudwatch/home"
    echo ""
    echo "=== Important Notes ==="
    echo "- The landing zone is now ready for account provisioning"
    echo "- Review and customize the organizational structure as needed"
    echo "- Configure additional security and compliance controls"
    echo "- Set up monitoring and alerting for your environment"
}

# Function to handle different actions
handle_action() {
    case $ACTION in
        "create")
            validate_template
            create_stack
            display_deployment_summary
            ;;
        "update")
            validate_template
            update_stack
            display_deployment_summary
            ;;
        "delete")
            delete_stack
            print_success "Stack deletion completed"
            ;;
        "validate")
            validate_template
            ;;
        *)
            print_error "No action specified. Use -c, -u, -d, or -v"
            usage
            exit 1
            ;;
    esac
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Landing Zone CloudFormation Deployment"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Check prerequisites
    check_prerequisites
    
    # Handle action
    handle_action
}

# Run main function
main "$@"
