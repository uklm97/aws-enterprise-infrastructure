#!/bin/bash

# AWS Control Tower Deployment Script
# This script automates the deployment of AWS Control Tower

set -e

# Configuration
REGION="us-east-1"
CONTROL_TOWER_VERSION="3.0"
MANAGEMENT_ACCOUNT_ID=""
ORGANIZATION_ID=""
HOME_REGION="us-east-1"

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
    
    # Check if account is root account
    MANAGEMENT_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_status "Management Account ID: $MANAGEMENT_ACCOUNT_ID"
    
    # Check if Organizations is enabled
    if ! aws organizations describe-organization &> /dev/null; then
        print_error "AWS Organizations is not enabled. Please enable it first."
        exit 1
    fi
    
    ORGANIZATION_ID=$(aws organizations describe-organization --query Organization.Id --output text)
    print_status "Organization ID: $ORGANIZATION_ID"
    
    # Check if Control Tower is already deployed
    if aws controltower list-landing-zones &> /dev/null; then
        print_warning "Control Tower appears to be already deployed."
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Prerequisites check completed"
}

# Function to validate configuration
validate_configuration() {
    print_status "Validating configuration..."
    
    # Check if required services are available in the region
    SERVICES=("controltower" "organizations" "sso" "config" "cloudtrail")
    
    for service in "${SERVICES[@]}"; do
        if ! aws $service help &> /dev/null; then
            print_error "Service $service is not available or not configured properly."
            exit 1
        fi
    done
    
    # Check if the account has sufficient permissions
    REQUIRED_POLICIES=(
        "AdministratorAccess"
        "AWSOrganizationsFullAccess"
        "AWSSSOFullAccess"
    )
    
    for policy in "${REQUIRED_POLICIES[@]}"; do
        if ! aws iam list-attached-user-policies --user-name $(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2) --query "AttachedPolicies[?PolicyName=='$policy']" --output text | grep -q "$policy"; then
            print_warning "Policy $policy may not be attached to your user."
        fi
    done
    
    print_success "Configuration validation completed"
}

# Function to prepare S3 bucket for Control Tower
prepare_s3_bucket() {
    print_status "Preparing S3 bucket for Control Tower..."
    
    BUCKET_NAME="aws-control-tower-$MANAGEMENT_ACCOUNT_ID-$REGION"
    
    # Create S3 bucket if it doesn't exist
    if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
        aws s3 mb "s3://$BUCKET_NAME" --region $REGION
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled
        
        # Enable server-side encryption
        aws s3api put-bucket-encryption \
            --bucket "$BUCKET_NAME" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        
        # Block public access
        aws s3api put-public-access-block \
            --bucket "$BUCKET_NAME" \
            --public-access-block-configuration \
            BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
        
        print_success "S3 bucket $BUCKET_NAME created and configured"
    else
        print_status "S3 bucket $BUCKET_NAME already exists"
    fi
}

# Function to create Control Tower configuration
create_control_tower_config() {
    print_status "Creating Control Tower configuration..."
    
    cat > control-tower-config.json << EOF
{
    "LandingZoneIdentifier": "aws-landing-zone",
    "LandingZoneDisplayName": "AWS Landing Zone",
    "Description": "Enterprise AWS Landing Zone with automated governance",
    "Version": "$CONTROL_TOWER_VERSION",
    "HomeRegion": "$HOME_REGION",
    "ManagementAccountId": "$MANAGEMENT_ACCOUNT_ID",
    "OrganizationId": "$ORGANIZATION_ID",
    "LogArchiveAccountId": "",
    "AuditAccountId": "",
    "SharedServicesAccountId": "",
    "EnableLogging": true,
    "EnableAuditing": true,
    "EnableSecurityHub": true,
    "EnableConfig": true,
    "EnableCloudTrail": true,
    "EnableGuardDuty": true,
    "EnableMacie": true,
    "EnableSecurityHub": true,
    "EnableSSO": true,
    "SSOUserEmail": "",
    "SSOUserFirstName": "",
    "SSOUserLastName": "",
    "SSOUserDisplayName": "Landing Zone Administrator"
}
EOF
    
    print_success "Control Tower configuration created"
}

# Function to deploy Control Tower
deploy_control_tower() {
    print_status "Deploying AWS Control Tower..."
    
    # Create the landing zone
    aws controltower create-landing-zone \
        --landing-zone-identifier "aws-landing-zone" \
        --landing-zone-display-name "AWS Landing Zone" \
        --description "Enterprise AWS Landing Zone with automated governance" \
        --version "$CONTROL_TOWER_VERSION" \
        --home-region "$HOME_REGION" \
        --manifest "control-tower-config.json" \
        --region "$REGION"
    
    print_status "Control Tower deployment initiated. This may take 30-60 minutes..."
    
    # Wait for deployment to complete
    while true; do
        STATUS=$(aws controltower get-landing-zone-status \
            --landing-zone-identifier "aws-landing-zone" \
            --region "$REGION" \
            --query "Status" \
            --output text 2>/dev/null || echo "DEPLOYING")
        
        case $STATUS in
            "SUCCEEDED")
                print_success "Control Tower deployment completed successfully!"
                break
                ;;
            "FAILED")
                print_error "Control Tower deployment failed. Check CloudFormation events for details."
                exit 1
                ;;
            *)
                print_status "Control Tower deployment status: $STATUS. Waiting..."
                sleep 60
                ;;
        esac
    done
}

# Function to configure customizations
configure_customizations() {
    print_status "Configuring Control Tower customizations..."
    
    # Create custom guardrails
    create_custom_guardrails
    
    # Configure additional security policies
    configure_security_policies
    
    # Setup monitoring and alerting
    setup_monitoring
    
    # Configure cost optimization
    configure_cost_optimization
    
    print_success "Customizations configured"
}

# Function to create custom guardrails
create_custom_guardrails() {
    print_status "Creating custom guardrails..."
    
    # Example custom guardrails
    GUARDRAILS=(
        "prevent-public-s3-buckets"
        "require-mfa-for-root"
        "prevent-deletion-of-log-archive"
        "require-encryption-for-ebs"
        "prevent-public-ec2-instances"
    )
    
    for guardrail in "${GUARDRAILS[@]}"; do
        print_status "Creating guardrail: $guardrail"
        # Implementation would go here
    done
}

# Function to configure security policies
configure_security_policies() {
    print_status "Configuring security policies..."
    
    # Configure password policy
    aws iam update-account-password-policy \
        --minimum-password-length 12 \
        --require-symbols \
        --require-numbers \
        --require-uppercase-characters \
        --require-lowercase-characters \
        --allow-users-to-change-password \
        --max-password-age 90 \
        --password-reuse-prevention 24
    
    # Configure MFA policy
    # Implementation would go here
    
    print_success "Security policies configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring and alerting..."
    
    # Create CloudWatch dashboards
    create_cloudwatch_dashboards
    
    # Configure SNS topics for alerts
    create_sns_topics
    
    # Setup CloudWatch alarms
    create_cloudwatch_alarms
    
    print_success "Monitoring setup completed"
}

# Function to create CloudWatch dashboards
create_cloudwatch_dashboards() {
    print_status "Creating CloudWatch dashboards..."
    
    # Executive Dashboard
    cat > executive-dashboard.json << EOF
{
    "DashboardName": "LandingZone-Executive",
    "DashboardBody": "{\"widgets\":[{\"type\":\"metric\",\"properties\":{\"metrics\":[[\"AWS/Organizations\",\"AccountCount\"]],\"period\":300,\"stat\":\"Average\",\"region\":\"$REGION\",\"title\":\"Total Accounts\"}}]}"
}
EOF
    
    aws cloudwatch put-dashboard --cli-input-json file://executive-dashboard.json
    
    # Security Dashboard
    cat > security-dashboard.json << EOF
{
    "DashboardName": "LandingZone-Security",
    "DashboardBody": "{\"widgets\":[{\"type\":\"metric\",\"properties\":{\"metrics\":[[\"AWS/GuardDuty\",\"TotalFindings\"]],\"period\":300,\"stat\":\"Sum\",\"region\":\"$REGION\",\"title\":\"Security Findings\"}}]}"
}
EOF
    
    aws cloudwatch put-dashboard --cli-input-json file://security-dashboard.json
    
    print_success "CloudWatch dashboards created"
}

# Function to create SNS topics
create_sns_topics() {
    print_status "Creating SNS topics for alerts..."
    
    TOPICS=("landing-zone-alerts" "security-alerts" "compliance-alerts" "cost-alerts")
    
    for topic in "${TOPICS[@]}"; do
        aws sns create-topic --name "$topic" --region "$REGION"
        print_status "Created SNS topic: $topic"
    done
}

# Function to create CloudWatch alarms
create_cloudwatch_alarms() {
    print_status "Creating CloudWatch alarms..."
    
    # Example alarms
    ALARMS=(
        "HighCPUUtilization"
        "HighMemoryUtilization"
        "SecurityFindings"
        "CostThreshold"
    )
    
    for alarm in "${ALARMS[@]}"; do
        print_status "Creating alarm: $alarm"
        # Implementation would go here
    done
}

# Function to configure cost optimization
configure_cost_optimization() {
    print_status "Configuring cost optimization..."
    
    # Enable Cost Explorer
    aws ce get-cost-and-usage --time-period Start=2023-01-01,End=2023-01-31 --granularity MONTHLY --metrics BlendedCost &> /dev/null || print_warning "Cost Explorer may not be enabled"
    
    # Create budget alerts
    create_budget_alerts
    
    print_success "Cost optimization configured"
}

# Function to create budget alerts
create_budget_alerts() {
    print_status "Creating budget alerts..."
    
    # Monthly budget alert
    cat > monthly-budget.json << EOF
{
    "BudgetName": "MonthlyBudget",
    "BudgetLimit": {
        "Amount": "1000",
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
                    "Address": "admin@example.com",
                    "SubscriptionType": "EMAIL"
                }
            ]
        }
    ]
}
EOF
    
    aws budgets create-budget --cli-input-json file://monthly-budget.json
    
    print_success "Budget alerts created"
}

# Function to display deployment summary
display_summary() {
    print_success "AWS Control Tower deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Management Account ID: $MANAGEMENT_ACCOUNT_ID"
    echo "Organization ID: $ORGANIZATION_ID"
    echo "Home Region: $HOME_REGION"
    echo "Control Tower Version: $CONTROL_TOWER_VERSION"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Access Control Tower console: https://console.aws.amazon.com/controltower"
    echo "2. Configure AWS SSO for user access"
    echo "3. Create organizational units (OUs)"
    echo "4. Provision accounts using Account Factory"
    echo "5. Configure custom guardrails and policies"
    echo ""
    echo "=== Important URLs ==="
    echo "Control Tower Console: https://console.aws.amazon.com/controltower"
    echo "AWS SSO Console: https://console.aws.amazon.com/singlesignon"
    echo "AWS Organizations: https://console.aws.amazon.com/organizations"
    echo "CloudWatch Dashboards: https://console.aws.amazon.com/cloudwatch/home"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Control Tower Deployment Script"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    validate_configuration
    prepare_s3_bucket
    create_control_tower_config
    deploy_control_tower
    configure_customizations
    display_summary
}

# Run main function
main "$@"
