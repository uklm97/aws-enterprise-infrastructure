#!/bin/bash

# AWS Operations Automation - Deployment Script
# This script deploys the complete automation framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="aws-operations-automation"
ENVIRONMENT="dev"
AWS_REGION="us-east-1"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    log_success "All prerequisites are satisfied"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found, skipping Python dependencies"
    fi
}

create_lambda_packages() {
    log_info "Creating Lambda function packages..."
    
    # Create lambda_functions directory
    mkdir -p lambda_functions
    
    # Package instance scheduler
    if [ -d "python/cost_management" ]; then
        cd python/cost_management
        zip -r ../../lambda_functions/instance_scheduler.zip scheduled_start_stop.py
        cd ../..
        log_success "Instance scheduler package created"
    fi
    
    # Package snapshot manager
    if [ -d "python/backup_recovery" ]; then
        cd python/backup_recovery
        zip -r ../../lambda_functions/snapshot_manager.zip snapshot_manager.py
        cd ../..
        log_success "Snapshot manager package created"
    fi
}

deploy_terraform() {
    log_info "Deploying Terraform infrastructure..."
    
    cd terraform
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var="project_name=$PROJECT_NAME" \
                   -var="environment=$ENVIRONMENT" \
                   -var="aws_region=$AWS_REGION" \
                   -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    # Get outputs
    log_info "Getting Terraform outputs..."
    terraform output
    
    cd ..
    
    log_success "Terraform infrastructure deployed"
}

setup_configuration() {
    log_info "Setting up configuration files..."
    
    # Create config directory
    mkdir -p config
    
    # Create automation config if it doesn't exist
    if [ ! -f "config/automation_config.yaml" ]; then
        cat > config/automation_config.yaml << EOF
# AWS Operations Automation Configuration

aws_region: $AWS_REGION
project_name: $PROJECT_NAME
environment: $ENVIRONMENT

# Instance scheduling configuration
schedules:
  business_hours:
    start_time: "08:00"
    stop_time: "18:00"
    timezone: "UTC"
  weekend_shutdown: true
  holiday_shutdown: true

# Instance tags for automation
instance_tags:
  start_tag: "AutoStart"
  stop_tag: "AutoStop"
  environment_tag: "Environment"

# Backup configuration
backup_schedules:
  daily:
    enabled: true
    time: "02:00"
    retention_days: 7
  weekly:
    enabled: true
    day: "sunday"
    time: "03:00"
    retention_days: 30
  monthly:
    enabled: true
    day: "1st"
    time: "04:00"
    retention_days: 90

# Cross-region backup
cross_region_backup:
  enabled: true
  destination_regions: ["us-west-2", "eu-west-1"]
  retention_days: 365

# Notifications
notifications:
  email: "admin@company.com"
  sns_topic: "aws-operations-alerts"

# Cost tracking
cost_tracking:
  enabled: true
  hourly_cost: 0.10

# Compliance
compliance:
  rto_hours: 4
  rpo_hours: 24
  encryption_required: true
EOF
        log_success "Configuration file created"
    else
        log_info "Configuration file already exists"
    fi
}

test_automation() {
    log_info "Testing automation functions..."
    
    # Test instance scheduler
    if [ -f "python/cost_management/scheduled_start_stop.py" ]; then
        log_info "Testing instance scheduler..."
        cd python/cost_management
        python3 -c "import scheduled_start_stop; print('Instance scheduler test passed')"
        cd ../..
    fi
    
    # Test snapshot manager
    if [ -f "python/backup_recovery/snapshot_manager.py" ]; then
        log_info "Testing snapshot manager..."
        cd python/backup_recovery
        python3 -c "import snapshot_manager; print('Snapshot manager test passed')"
        cd ../..
    fi
    
    log_success "Automation functions tested successfully"
}

show_next_steps() {
    log_info "Deployment completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Tag your EC2 instances with 'AutoStart=true' and 'AutoStop=true' for scheduling"
    echo "2. Tag your EBS volumes with 'Backup=true' for automated snapshots"
    echo "3. Configure your notification email in the SNS topic"
    echo "4. Monitor the automation in CloudWatch dashboard"
    echo "5. Review the automation logs in CloudWatch Logs"
    echo
    echo "Useful commands:"
    echo "- Check automation status: aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/$PROJECT_NAME'"
    echo "- View automation dashboard: aws cloudwatch get-dashboard --dashboard-name '$PROJECT_NAME-automation-dashboard'"
    echo "- Test instance start: aws lambda invoke --function-name '$PROJECT_NAME-instance-scheduler' --payload '{\"action\":\"start\"}'"
    echo "- Test backup creation: aws lambda invoke --function-name '$PROJECT_NAME-snapshot-manager' --payload '{\"action\":\"daily_backup\"}'"
}

# Main deployment process
main() {
    echo "=========================================="
    echo "AWS Operations Automation - Deployment"
    echo "=========================================="
    echo
    
    check_prerequisites
    install_python_dependencies
    create_lambda_packages
    setup_configuration
    deploy_terraform
    test_automation
    show_next_steps
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
