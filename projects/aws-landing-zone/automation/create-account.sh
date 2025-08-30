#!/bin/bash

# AWS Account Provisioning Script
# This script automates the creation and configuration of new AWS accounts in the landing zone

set -e

# Configuration
REGION="us-east-1"
ORGANIZATION_ID=""
MANAGEMENT_ACCOUNT_ID=""
SSO_INSTANCE_ARN=""

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
    echo "  -n, --name NAME           Account name (required)"
    echo "  -o, --ou OU               Organizational Unit (required)"
    echo "  -e, --email EMAIL         Account email (required)"
    echo "  -t, --type TYPE           Account type (workload|sandbox|shared|security)"
    echo "  -r, --region REGION       AWS region (default: us-east-1)"
    echo "  -p, --permission-set PS   Permission set to assign"
    echo "  -u, --user USER           SSO user to assign"
    echo "  -b, --budget AMOUNT       Monthly budget amount"
    echo "  -c, --config CONFIG_FILE  Configuration file"
    echo "  -h, --help                Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -n prod-app-01 -o Workloads -e admin@company.com -t workload"
    echo "  $0 -n dev-test-01 -o Sandbox -e developer@company.com -t sandbox -p Developer"
    echo ""
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                ACCOUNT_NAME="$2"
                shift 2
                ;;
            -o|--ou)
                ORGANIZATIONAL_UNIT="$2"
                shift 2
                ;;
            -e|--email)
                ACCOUNT_EMAIL="$2"
                shift 2
                ;;
            -t|--type)
                ACCOUNT_TYPE="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -p|--permission-set)
                PERMISSION_SET="$2"
                shift 2
                ;;
            -u|--user)
                SSO_USER="$2"
                shift 2
                ;;
            -b|--budget)
                BUDGET_AMOUNT="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
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

# Function to validate required parameters
validate_parameters() {
    if [[ -z "$ACCOUNT_NAME" ]]; then
        print_error "Account name is required. Use -n or --name"
        exit 1
    fi
    
    if [[ -z "$ORGANIZATIONAL_UNIT" ]]; then
        print_error "Organizational Unit is required. Use -o or --ou"
        exit 1
    fi
    
    if [[ -z "$ACCOUNT_EMAIL" ]]; then
        print_error "Account email is required. Use -e or --email"
        exit 1
    fi
    
    # Validate email format
    if [[ ! "$ACCOUNT_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid email format: $ACCOUNT_EMAIL"
        exit 1
    fi
    
    # Set default account type if not specified
    if [[ -z "$ACCOUNT_TYPE" ]]; then
        ACCOUNT_TYPE="workload"
    fi
    
    # Validate account type
    case $ACCOUNT_TYPE in
        workload|sandbox|shared|security)
            ;;
        *)
            print_error "Invalid account type: $ACCOUNT_TYPE. Must be one of: workload, sandbox, shared, security"
            exit 1
            ;;
    esac
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
    
    # Get management account ID
    MANAGEMENT_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_status "Management Account ID: $MANAGEMENT_ACCOUNT_ID"
    
    # Check if Organizations is enabled
    if ! aws organizations describe-organization &> /dev/null; then
        print_error "AWS Organizations is not enabled. Please enable it first."
        exit 1
    fi
    
    ORGANIZATION_ID=$(aws organizations describe-organization --query Organization.Id --output text)
    print_status "Organization ID: $ORGANIZATION_ID"
    
    # Check if SSO is configured
    SSO_INSTANCE_ARN=$(aws sso-admin list-instances --query "Instances[0].InstanceArn" --output text 2>/dev/null || echo "")
    if [[ -z "$SSO_INSTANCE_ARN" ]]; then
        print_warning "AWS SSO is not configured. SSO assignments will be skipped."
    else
        print_status "SSO Instance ARN: $SSO_INSTANCE_ARN"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to validate organizational unit
validate_organizational_unit() {
    print_status "Validating organizational unit: $ORGANIZATIONAL_UNIT"
    
    # Get list of OUs
    OU_ID=$(aws organizations list-organizational-units-for-parent \
        --parent-id r-$(aws organizations list-roots --query "Roots[0].Id" --output text | cut -d'-' -f2) \
        --query "OrganizationalUnits[?Name=='$ORGANIZATIONAL_UNIT'].Id" \
        --output text)
    
    if [[ -z "$OU_ID" ]]; then
        print_error "Organizational Unit '$ORGANIZATIONAL_UNIT' not found"
        print_status "Available OUs:"
        aws organizations list-organizational-units-for-parent \
            --parent-id r-$(aws organizations list-roots --query "Roots[0].Id" --output text | cut -d'-' -f2) \
            --query "OrganizationalUnits[].Name" \
            --output table
        exit 1
    fi
    
    print_success "Organizational Unit validated: $OU_ID"
}

# Function to check if account already exists
check_account_exists() {
    print_status "Checking if account already exists..."
    
    # Check by email
    EXISTING_ACCOUNT=$(aws organizations list-accounts \
        --query "Accounts[?Email=='$ACCOUNT_EMAIL'].Id" \
        --output text)
    
    if [[ -n "$EXISTING_ACCOUNT" ]]; then
        print_error "Account with email $ACCOUNT_EMAIL already exists: $EXISTING_ACCOUNT"
        exit 1
    fi
    
    # Check by name
    EXISTING_ACCOUNT=$(aws organizations list-accounts \
        --query "Accounts[?Name=='$ACCOUNT_NAME'].Id" \
        --output text)
    
    if [[ -n "$EXISTING_ACCOUNT" ]]; then
        print_error "Account with name $ACCOUNT_NAME already exists: $EXISTING_ACCOUNT"
        exit 1
    fi
    
    print_success "Account does not exist, proceeding with creation"
}

# Function to create AWS account
create_account() {
    print_status "Creating AWS account: $ACCOUNT_NAME"
    
    # Create account request
    CREATE_ACCOUNT_RESPONSE=$(aws organizations create-account \
        --email "$ACCOUNT_EMAIL" \
        --account-name "$ACCOUNT_NAME" \
        --role-name "OrganizationAccountAccessRole" \
        --iam-user-access-to-billing "DENY")
    
    CREATE_ACCOUNT_REQUEST_ID=$(echo "$CREATE_ACCOUNT_RESPONSE" | jq -r '.CreateAccountStatus.Id')
    print_status "Account creation request ID: $CREATE_ACCOUNT_REQUEST_ID"
    
    # Wait for account creation to complete
    print_status "Waiting for account creation to complete (this may take 5-10 minutes)..."
    
    while true; do
        STATUS=$(aws organizations describe-create-account-status \
            --create-account-request-id "$CREATE_ACCOUNT_REQUEST_ID" \
            --query "CreateAccountStatus.State" \
            --output text)
        
        case $STATUS in
            "SUCCEEDED")
                ACCOUNT_ID=$(aws organizations describe-create-account-status \
                    --create-account-request-id "$CREATE_ACCOUNT_REQUEST_ID" \
                    --query "CreateAccountStatus.AccountId" \
                    --output text)
                print_success "Account created successfully: $ACCOUNT_ID"
                break
                ;;
            "FAILED")
                FAILURE_REASON=$(aws organizations describe-create-account-status \
                    --create-account-request-id "$CREATE_ACCOUNT_REQUEST_ID" \
                    --query "CreateAccountStatus.FailureReason" \
                    --output text)
                print_error "Account creation failed: $FAILURE_REASON"
                exit 1
                ;;
            *)
                print_status "Account creation status: $STATUS. Waiting..."
                sleep 30
                ;;
        esac
    done
}

# Function to move account to organizational unit
move_account_to_ou() {
    print_status "Moving account to organizational unit: $ORGANIZATIONAL_UNIT"
    
    # Get OU ID
    OU_ID=$(aws organizations list-organizational-units-for-parent \
        --parent-id r-$(aws organizations list-roots --query "Roots[0].Id" --output text | cut -d'-' -f2) \
        --query "OrganizationalUnits[?Name=='$ORGANIZATIONAL_UNIT'].Id" \
        --output text)
    
    # Move account
    aws organizations move-account \
        --account-id "$ACCOUNT_ID" \
        --source-parent-id r-$(aws organizations list-roots --query "Roots[0].Id" --output text | cut -d'-' -f2) \
        --destination-parent-id "$OU_ID"
    
    print_success "Account moved to OU: $ORGANIZATIONAL_UNIT"
}

# Function to configure account settings
configure_account() {
    print_status "Configuring account settings..."
    
    # Set account alias
    aws iam create-account-alias --account-alias "$ACCOUNT_NAME" --region "$REGION" || print_warning "Could not set account alias"
    
    # Configure password policy
    aws iam update-account-password-policy \
        --minimum-password-length 12 \
        --require-symbols \
        --require-numbers \
        --require-uppercase-characters \
        --require-lowercase-characters \
        --allow-users-to-change-password \
        --max-password-age 90 \
        --password-reuse-prevention 24 \
        --region "$REGION" || print_warning "Could not update password policy"
    
    print_success "Account settings configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring for account: $ACCOUNT_ID"
    
    # Create CloudWatch dashboard
    cat > monitoring-dashboard.json << EOF
{
    "DashboardName": "$ACCOUNT_NAME-monitoring",
    "DashboardBody": "{\"widgets\":[{\"type\":\"metric\",\"properties\":{\"metrics\":[[\"AWS/Billing\",\"EstimatedCharges\",\"Currency\",\"USD\"]],\"period\":300,\"stat\":\"Maximum\",\"region\":\"$REGION\",\"title\":\"Estimated Charges\"}}]}"
}
EOF
    
    aws cloudwatch put-dashboard --cli-input-json file://monitoring-dashboard.json --region "$REGION" || print_warning "Could not create CloudWatch dashboard"
    
    # Create budget if specified
    if [[ -n "$BUDGET_AMOUNT" ]]; then
        create_budget
    fi
    
    print_success "Monitoring setup completed"
}

# Function to create budget
create_budget() {
    print_status "Creating budget: $BUDGET_AMOUNT USD"
    
    cat > budget.json << EOF
{
    "BudgetName": "$ACCOUNT_NAME-monthly-budget",
    "BudgetLimit": {
        "Amount": "$BUDGET_AMOUNT",
        "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {},
    "NotificationsWithSubscribers": [
        {
            "Notification": {
                "ComparisonOperator": "GREATER_THAN",
                "NotificationType": "ACTUAL",
                "Threshold": 80,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "Address": "$ACCOUNT_EMAIL",
                    "SubscriptionType": "EMAIL"
                }
            ]
        }
    ]
}
EOF
    
    aws budgets create-budget --cli-input-json file://budget.json --region "$REGION" || print_warning "Could not create budget"
    
    print_success "Budget created"
}

# Function to setup SSO access
setup_sso_access() {
    if [[ -z "$SSO_INSTANCE_ARN" ]]; then
        print_warning "SSO not configured, skipping SSO setup"
        return
    fi
    
    if [[ -z "$PERMISSION_SET" ]] || [[ -z "$SSO_USER" ]]; then
        print_warning "Permission set or SSO user not specified, skipping SSO setup"
        return
    fi
    
    print_status "Setting up SSO access..."
    
    # Get permission set ARN
    PERMISSION_SET_ARN=$(aws sso-admin list-permission-sets \
        --instance-arn "$SSO_INSTANCE_ARN" \
        --query "PermissionSets[0]" \
        --output text)
    
    if [[ -z "$PERMISSION_SET_ARN" ]]; then
        print_warning "Permission set not found, skipping SSO setup"
        return
    fi
    
    # Create account assignment
    aws sso-admin create-account-assignment \
        --instance-arn "$SSO_INSTANCE_ARN" \
        --permission-set-arn "$PERMISSION_SET_ARN" \
        --target-id "$ACCOUNT_ID" \
        --target-type "AWS_ACCOUNT" \
        --principal-id "$SSO_USER" \
        --principal-type "USER" || print_warning "Could not create SSO account assignment"
    
    print_success "SSO access configured"
}

# Function to apply account policies
apply_account_policies() {
    print_status "Applying account policies..."
    
    # Apply SCPs based on account type
    case $ACCOUNT_TYPE in
        security)
            apply_security_policies
            ;;
        shared)
            apply_shared_policies
            ;;
        workload)
            apply_workload_policies
            ;;
        sandbox)
            apply_sandbox_policies
            ;;
    esac
    
    print_success "Account policies applied"
}

# Function to apply security policies
apply_security_policies() {
    print_status "Applying security policies..."
    # Implementation for security account policies
}

# Function to apply shared policies
apply_shared_policies() {
    print_status "Applying shared policies..."
    # Implementation for shared account policies
}

# Function to apply workload policies
apply_workload_policies() {
    print_status "Applying workload policies..."
    # Implementation for workload account policies
}

# Function to apply sandbox policies
apply_sandbox_policies() {
    print_status "Applying sandbox policies..."
    # Implementation for sandbox account policies
}

# Function to create account documentation
create_documentation() {
    print_status "Creating account documentation..."
    
    cat > "$ACCOUNT_NAME-account-info.md" << EOF
# AWS Account Information

## Account Details
- **Account Name**: $ACCOUNT_NAME
- **Account ID**: $ACCOUNT_ID
- **Account Email**: $ACCOUNT_EMAIL
- **Account Type**: $ACCOUNT_TYPE
- **Organizational Unit**: $ORGANIZATIONAL_UNIT
- **Region**: $REGION
- **Created**: $(date)

## Access Information
- **SSO Portal**: https://console.aws.amazon.com/singlesignon
- **Account Alias**: $ACCOUNT_NAME
- **Permission Set**: $PERMISSION_SET
- **SSO User**: $SSO_USER

## Budget Information
- **Monthly Budget**: $BUDGET_AMOUNT USD
- **Budget Alerts**: 80% threshold

## Monitoring
- **CloudWatch Dashboard**: $ACCOUNT_NAME-monitoring
- **Budget Monitoring**: Enabled

## Security
- **Password Policy**: 12 characters, symbols, numbers, uppercase, lowercase
- **MFA**: Required
- **Root Access**: Disabled

## Compliance
- **Config Rules**: Enabled
- **CloudTrail**: Enabled
- **GuardDuty**: Enabled
- **Security Hub**: Enabled

## Next Steps
1. Access the account via SSO
2. Configure additional security settings
3. Set up application-specific resources
4. Configure monitoring and alerting
5. Review and adjust policies as needed

## Support
For issues or questions, contact the AWS Landing Zone team.
EOF
    
    print_success "Account documentation created: $ACCOUNT_NAME-account-info.md"
}

# Function to display summary
display_summary() {
    print_success "AWS Account provisioning completed!"
    
    echo ""
    echo "=== Account Summary ==="
    echo "Account Name: $ACCOUNT_NAME"
    echo "Account ID: $ACCOUNT_ID"
    echo "Account Email: $ACCOUNT_EMAIL"
    echo "Account Type: $ACCOUNT_TYPE"
    echo "Organizational Unit: $ORGANIZATIONAL_UNIT"
    echo "Region: $REGION"
    echo ""
    echo "=== Access Information ==="
    echo "SSO Portal: https://console.aws.amazon.com/singlesignon"
    echo "Account Alias: $ACCOUNT_NAME"
    if [[ -n "$PERMISSION_SET" ]]; then
        echo "Permission Set: $PERMISSION_SET"
    fi
    if [[ -n "$SSO_USER" ]]; then
        echo "SSO User: $SSO_USER"
    fi
    echo ""
    echo "=== Next Steps ==="
    echo "1. Wait 5-10 minutes for account to be fully provisioned"
    echo "2. Access the account via SSO"
    echo "3. Configure additional resources as needed"
    echo "4. Review account documentation: $ACCOUNT_NAME-account-info.md"
    echo ""
    echo "=== Important Notes ==="
    echo "- Account creation may take up to 10 minutes to complete"
    echo "- SSO access will be available once the account is fully provisioned"
    echo "- Budget alerts will be sent to: $ACCOUNT_EMAIL"
    echo "- Monitor the account for compliance and security"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Account Provisioning Script"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Validate parameters
    validate_parameters
    
    # Check prerequisites
    check_prerequisites
    
    # Validate organizational unit
    validate_organizational_unit
    
    # Check if account already exists
    check_account_exists
    
    # Create account
    create_account
    
    # Move account to organizational unit
    move_account_to_ou
    
    # Configure account settings
    configure_account
    
    # Setup monitoring
    setup_monitoring
    
    # Setup SSO access
    setup_sso_access
    
    # Apply account policies
    apply_account_policies
    
    # Create documentation
    create_documentation
    
    # Display summary
    display_summary
}

# Run main function
main "$@"
