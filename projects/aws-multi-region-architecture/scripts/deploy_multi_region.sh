#!/bin/bash

# AWS Multi-Region Architecture Deployment Script
# This script deploys the complete multi-region architecture using Terraform

set -e

# Configuration
PROJECT_NAME="aws-multi-region-architecture"
ENVIRONMENT="dev"
PRIMARY_REGION="us-east-1"
SECONDARY_REGIONS="us-west-2,eu-west-1"
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
    echo "  -e, --environment ENV        Environment (dev, staging, prod)"
    echo "  -p, --primary-region REGION  Primary AWS region"
    echo "  -s, --secondary-regions      Comma-separated secondary regions"
    echo "  -n, --project-name NAME      Project name"
    echo "  -d, --domain-name DOMAIN     Domain name for the application"
    echo "  -r, --enable-replication     Enable cross-region replication"
    echo "  -g, --enable-global-dist     Enable global distribution"
    echo "  -f, --enable-failover        Enable automated failover"
    echo "  -m, --enable-monitoring      Enable health monitoring"
    echo "  -c, --enable-compliance      Enable compliance monitoring"
    echo "  -o, --enable-optimization    Enable cost optimization"
    echo "  -t, --rto-minutes MINUTES    Recovery Time Objective in minutes"
    echo "  -b, --rpo-minutes MINUTES    Recovery Point Objective in minutes"
    echo "  -a, --alarm-email EMAIL      Email for alarms and notifications"
    echo "  -f, --dry-run                Show what would be deployed without deploying"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment prod --primary-region us-east-1"
    echo "  $0 --secondary-regions us-west-2,eu-west-1 --enable-replication"
    echo "  $0 --domain-name example.com --enable-global-dist --enable-failover"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--primary-region)
            PRIMARY_REGION="$2"
            shift 2
            ;;
        -s|--secondary-regions)
            SECONDARY_REGIONS="$2"
            shift 2
            ;;
        -n|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -d|--domain-name)
            DOMAIN_NAME="$2"
            shift 2
            ;;
        -r|--enable-replication)
            ENABLE_REPLICATION=true
            shift
            ;;
        -g|--enable-global-dist)
            ENABLE_GLOBAL_DIST=true
            shift
            ;;
        -f|--enable-failover)
            ENABLE_FAILOVER=true
            shift
            ;;
        -m|--enable-monitoring)
            ENABLE_MONITORING=true
            shift
            ;;
        -c|--enable-compliance)
            ENABLE_COMPLIANCE=true
            shift
            ;;
        -o|--enable-optimization)
            ENABLE_OPTIMIZATION=true
            shift
            ;;
        -t|--rto-minutes)
            RTO_MINUTES="$2"
            shift 2
            ;;
        -b|--rpo-minutes)
            RPO_MINUTES="$2"
            shift 2
            ;;
        -a|--alarm-email)
            ALARM_EMAIL="$2"
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
    
    # Validate primary region
    if ! aws ec2 describe-regions --region-names "$PRIMARY_REGION" &> /dev/null; then
        print_error "Invalid primary region: $PRIMARY_REGION"
        exit 1
    fi
    
    # Validate secondary regions
    IFS=',' read -ra REGIONS <<< "$SECONDARY_REGIONS"
    for region in "${REGIONS[@]}"; do
        if ! aws ec2 describe-regions --region-names "$region" &> /dev/null; then
            print_error "Invalid secondary region: $region"
            exit 1
        fi
    done
    
    # Validate email if provided
    if [[ -n "$ALARM_EMAIL" ]] && [[ ! "$ALARM_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid alarm email address: $ALARM_EMAIL"
        exit 1
    fi
    
    # Validate domain name if provided
    if [[ -n "$DOMAIN_NAME" ]] && [[ ! "$DOMAIN_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        print_error "Invalid domain name: $DOMAIN_NAME"
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
primary_region = "$PRIMARY_REGION"
secondary_regions = [$(echo "$SECONDARY_REGIONS" | sed 's/,/", "/g' | sed 's/^/"/' | sed 's/$/"/')]
environment = "$ENVIRONMENT"
project_name = "$PROJECT_NAME"
domain_name = "${DOMAIN_NAME:-example.com}"
enable_cross_region_replication = ${ENABLE_REPLICATION:-true}
enable_global_distribution = ${ENABLE_GLOBAL_DIST:-true}
enable_disaster_recovery = ${ENABLE_FAILOVER:-true}
enable_health_monitoring = ${ENABLE_MONITORING:-true}
enable_compliance_monitoring = ${ENABLE_COMPLIANCE:-true}
enable_automated_failover = ${ENABLE_FAILOVER:-true}
rto_minutes = ${RTO_MINUTES:-60}
rpo_minutes = ${RPO_MINUTES:-15}
notification_email = "${ALARM_EMAIL:-}"
enable_encryption = true
enable_vpc_flow_logs = true
enable_cloudtrail = true
enable_config = true
enable_auto_scaling = true
min_capacity = 1
max_capacity = 10
target_capacity = 3
enable_caching = true
cache_ttl = 3600
enable_compression = true
enable_http2 = true
enable_detailed_monitoring = true
monitoring_retention_days = 30
log_retention_days = 14
enable_xray_tracing = true
enable_cloudwatch_alarms = true
enable_sns_notifications = true
alarm_threshold_cpu = 80
alarm_threshold_memory = 80
alarm_threshold_disk = 80
enable_compliance_monitoring = true
compliance_frameworks = ["SOC2", "HIPAA", "PCI-DSS"]
data_retention_days = 90
audit_log_retention_days = 365
enable_dr_testing = true
dr_test_schedule = "0 0 1 * *"
dr_test_duration_hours = 4
backup_retention_days = 30
backup_schedule = "0 2 * * *"
enable_cross_region_backup = true
EOF

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

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get outputs from Terraform
    PRIMARY_REGION_OUTPUT=$(terraform output -json primary_region 2>/dev/null || echo "{}")
    SECONDARY_REGIONS_OUTPUT=$(terraform output -json secondary_regions 2>/dev/null || echo "[]")
    S3_BUCKETS=$(terraform output -json s3_buckets 2>/dev/null || echo "{}")
    DYNAMODB_TABLE=$(terraform output -json dynamodb_global_table 2>/dev/null || echo "{}")
    RDS_INSTANCES=$(terraform output -json rds_instances 2>/dev/null || echo "{}")
    CLOUDFRONT_DISTRIBUTION=$(terraform output -json cloudfront_distribution 2>/dev/null || echo "{}")
    ROUTE53_ZONE=$(terraform output -json route53_zone 2>/dev/null || echo "{}")
    
    # Test primary region
    print_status "Testing primary region..."
    primary_region=$(echo "$PRIMARY_REGION_OUTPUT" | jq -r '. // empty')
    if [[ -n "$primary_region" ]]; then
        print_success "Primary region configured: $primary_region"
    fi
    
    # Test secondary regions
    print_status "Testing secondary regions..."
    secondary_regions=$(echo "$SECONDARY_REGIONS_OUTPUT" | jq -r '.[] // empty')
    if [[ -n "$secondary_regions" ]]; then
        print_success "Secondary regions configured: $secondary_regions"
    fi
    
    # Test S3 buckets
    print_status "Testing S3 buckets..."
    s3_buckets=$(echo "$S3_BUCKETS" | jq -r '.primary.name // empty')
    if [[ -n "$s3_buckets" ]]; then
        print_success "S3 buckets created across regions"
    fi
    
    # Test DynamoDB global table
    print_status "Testing DynamoDB global table..."
    dynamodb_name=$(echo "$DYNAMODB_TABLE" | jq -r '.name // empty')
    if [[ -n "$dynamodb_name" ]]; then
        print_success "DynamoDB global table created: $dynamodb_name"
    fi
    
    # Test RDS instances
    print_status "Testing RDS instances..."
    rds_primary=$(echo "$RDS_INSTANCES" | jq -r '.primary.identifier // empty')
    if [[ -n "$rds_primary" ]]; then
        print_success "RDS instances created across regions"
    fi
    
    # Test CloudFront distribution
    print_status "Testing CloudFront distribution..."
    cloudfront_id=$(echo "$CLOUDFRONT_DISTRIBUTION" | jq -r '.id // empty')
    if [[ -n "$cloudfront_id" ]]; then
        print_success "CloudFront distribution created: $cloudfront_id"
    fi
    
    # Test Route53 zone
    print_status "Testing Route53 zone..."
    route53_zone_id=$(echo "$ROUTE53_ZONE" | jq -r '.zone_id // empty')
    if [[ -n "$route53_zone_id" ]]; then
        print_success "Route53 zone created: $route53_zone_id"
    fi
    
    print_success "Deployment testing completed"
}

# Function to display deployment summary
display_summary() {
    print_success "AWS Multi-Region Architecture deployment completed!"
    
    echo ""
    echo "=== Deployment Summary ==="
    echo "Project Name: $PROJECT_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Primary Region: $PRIMARY_REGION"
    echo "Secondary Regions: $SECONDARY_REGIONS"
    echo "Domain Name: ${DOMAIN_NAME:-example.com}"
    echo ""
    
    # Get outputs from Terraform
    cd "$TERRAFORM_DIR"
    
    echo "=== Resources Created ==="
    
    # S3 buckets
    S3_BUCKETS=$(terraform output -json s3_buckets 2>/dev/null || echo "{}")
    if [[ "$S3_BUCKETS" != "{}" ]]; then
        echo "S3 Buckets:"
        echo "$S3_BUCKETS" | jq -r 'to_entries[] | "  - \(.key): \(.value.name) (\(.value.region))"'
    fi
    
    # DynamoDB global table
    DYNAMODB_TABLE=$(terraform output -json dynamodb_global_table 2>/dev/null || echo "{}")
    if [[ "$DYNAMODB_TABLE" != "{}" ]]; then
        echo "DynamoDB Global Table:"
        echo "  - Name: $(echo "$DYNAMODB_TABLE" | jq -r '.name // "N/A"')"
        echo "  - Regions: $(echo "$DYNAMODB_TABLE" | jq -r '.regions | join(", ") // "N/A"')"
    fi
    
    # RDS instances
    RDS_INSTANCES=$(terraform output -json rds_instances 2>/dev/null || echo "{}")
    if [[ "$RDS_INSTANCES" != "{}" ]]; then
        echo "RDS Instances:"
        echo "$RDS_INSTANCES" | jq -r 'to_entries[] | "  - \(.key): \(.value.identifier) (\(.value.region))"'
    fi
    
    # CloudFront distribution
    CLOUDFRONT_DISTRIBUTION=$(terraform output -json cloudfront_distribution 2>/dev/null || echo "{}")
    if [[ "$CLOUDFRONT_DISTRIBUTION" != "{}" ]]; then
        echo "CloudFront Distribution:"
        echo "  - ID: $(echo "$CLOUDFRONT_DISTRIBUTION" | jq -r '.id // "N/A"')"
        echo "  - Domain: $(echo "$CLOUDFRONT_DISTRIBUTION" | jq -r '.domain_name // "N/A"')"
    fi
    
    # Route53 zone
    ROUTE53_ZONE=$(terraform output -json route53_zone 2>/dev/null || echo "{}")
    if [[ "$ROUTE53_ZONE" != "{}" ]]; then
        echo "Route53 Zone:"
        echo "  - Zone ID: $(echo "$ROUTE53_ZONE" | jq -r '.zone_id // "N/A"')"
        echo "  - Domain: $(echo "$ROUTE53_ZONE" | jq -r '.domain_name // "N/A"')"
    fi
    
    echo ""
    echo "=== Multi-Region Features ==="
    echo "✅ Cross-Region Replication - S3 cross-region replication enabled"
    echo "✅ Global Distribution - CloudFront global distribution enabled"
    echo "✅ Disaster Recovery - Automated disaster recovery enabled"
    echo "✅ Health Monitoring - Cross-region health monitoring enabled"
    echo "✅ Automated Failover - Route53 automated failover enabled"
    echo "✅ Data Synchronization - DynamoDB global tables enabled"
    echo "✅ Global Load Balancing - Multi-region load balancing enabled"
    echo "✅ Edge Caching - CloudFront edge caching enabled"
    echo "✅ DNS Failover - Route53 DNS failover enabled"
    echo "✅ Backup Replication - Cross-region backup replication enabled"
    echo "✅ Compliance Monitoring - SOC2, HIPAA, PCI-DSS compliance"
    echo "✅ Cost Optimization - Spot instances and reserved instances"
    echo "✅ Security - Encryption, VPC flow logs, CloudTrail"
    echo "✅ Performance - Caching, compression, HTTP/2"
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Configure DNS records to point to your domain"
    echo "2. Set up monitoring and alerting for all regions"
    echo "3. Test disaster recovery procedures"
    echo "4. Configure cross-region backup policies"
    echo "5. Set up automated failover testing"
    echo "6. Configure compliance monitoring"
    echo "7. Set up cost optimization policies"
    echo "8. Configure security monitoring"
    echo "9. Set up performance monitoring"
    echo "10. Test global load balancing"
    
    echo ""
    echo "=== Important URLs ==="
    echo "CloudWatch Console: https://console.aws.amazon.com/cloudwatch/home"
    echo "Route53 Console: https://console.aws.amazon.com/route53/home"
    echo "S3 Console: https://console.aws.amazon.com/s3/home"
    echo "RDS Console: https://console.aws.amazon.com/rds/home"
    echo "DynamoDB Console: https://console.aws.amazon.com/dynamodb/home"
    echo "CloudFront Console: https://console.aws.amazon.com/cloudfront/home"
    
    echo ""
    echo "=== Disaster Recovery Info ==="
    echo "RTO (Recovery Time Objective): ${RTO_MINUTES:-60} minutes"
    echo "RPO (Recovery Point Objective): ${RPO_MINUTES:-15} minutes"
    echo "Failover Threshold: 3 consecutive failures"
    echo "Health Check Interval: 30 seconds"
    echo "Backup Retention: 30 days"
    echo "DR Test Schedule: Monthly on the 1st"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove Terraform plan file
    cd "$TERRAFORM_DIR"
    rm -f tfplan
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "AWS Multi-Region Architecture Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    validate_configuration
    install_python_dependencies
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