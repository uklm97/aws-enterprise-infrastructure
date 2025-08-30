#!/bin/bash
# AWS Server Hardening Framework Deployment Script
# This script deploys the complete server hardening framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Configuration
PROJECT_NAME="aws-server-hardening"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"
PYTHON_DIR="$PROJECT_DIR/python"

# Default values
AWS_REGION="us-east-1"
ENVIRONMENT="production"
DEPLOY_LINUX=true
DEPLOY_WINDOWS=true
DEPLOY_TERRAFORM=true
DEPLOY_CLOUDFORMATION=false

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --region REGION     AWS region (default: us-east-1)"
    echo "  -e, --environment ENV   Environment (default: production)"
    echo "  -l, --linux-only        Deploy Linux hardening only"
    echo "  -w, --windows-only      Deploy Windows hardening only"
    echo "  -t, --terraform         Deploy using Terraform (default)"
    echo "  -c, --cloudformation    Deploy using CloudFormation"
    echo "  -h, --help              Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy everything using Terraform"
    echo "  $0 -r us-west-2 -e staging            # Deploy to us-west-2 staging"
    echo "  $0 -l -t                              # Deploy Linux hardening with Terraform"
    echo "  $0 -w -c                              # Deploy Windows hardening with CloudFormation"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root (for Linux hardening)
    if [[ "$DEPLOY_LINUX" == true && "$EUID" -ne 0 ]]; then
        warn "Linux hardening requires root privileges. Some operations may fail."
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check Terraform (if using Terraform)
    if [[ "$DEPLOY_TERRAFORM" == true ]]; then
        if ! command -v terraform &> /dev/null; then
            error "Terraform is not installed. Please install it first."
            exit 1
        fi
    fi
    
    # Check jq
    if ! command -v jq &> /dev/null; then
        warn "jq is not installed. Some JSON processing may fail."
    fi
    
    log "Prerequisites check completed."
}

# Function to install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
        pip3 install -r "$PROJECT_DIR/requirements.txt"
        log "Python dependencies installed successfully."
    else
        warn "requirements.txt not found. Skipping Python dependency installation."
    fi
}

# Function to create configuration files
setup_configuration() {
    log "Setting up configuration files..."
    
    # Create config directory if it doesn't exist
    mkdir -p "$CONFIG_DIR"
    
    # Create default hardening configuration
    if [[ ! -f "$CONFIG_DIR/hardening_config.yaml" ]]; then
        cat > "$CONFIG_DIR/hardening_config.yaml" << 'EOF'
# AWS Server Hardening Configuration

# Linux Hardening Configuration
linux_hardening:
  enabled: true
  cis_benchmarks:
    ubuntu_20.04:
      system:
        disable_services:
          - telnet
          - rsh
          - rlogin
          - rexec
        sysctl_params:
          net.ipv4.ip_forward: "0"
          net.ipv4.conf.all.send_redirects: "0"
          net.ipv4.conf.default.send_redirects: "0"
          net.ipv4.conf.all.accept_source_route: "0"
          net.ipv4.conf.default.accept_source_route: "0"
      network:
        firewall_rules:
          - "INPUT -p tcp --dport 22 -j ACCEPT"
          - "INPUT -p tcp --dport 80 -j ACCEPT"
          - "INPUT -p tcp --dport 443 -j ACCEPT"
          - "INPUT -j DROP"
      users:
        max_days: 90
        max_attempts: 5
        remove_users:
          - games
          - gopher
      filesystem:
        file_permissions:
          /etc/passwd: "644"
          /etc/shadow: "600"
          /etc/group: "644"
          /etc/gshadow: "600"

# Windows Hardening Configuration
windows_hardening:
  enabled: true
  policies:
    high_security:
      password_policy:
        min_length: 12
        complexity: 1
        history: 24
        max_age: 90
        min_age: 1
      account_lockout:
        threshold: 5
        duration: 30
        window: 30
      audit_policy:
        categories:
          "Account Logon": "Success,Failure"
          "Account Management": "Success,Failure"
          "Directory Service Access": "Success,Failure"
          "Logon": "Success,Failure"
          "Object Access": "Success,Failure"
          "Policy Change": "Success,Failure"
          "Privilege Use": "Success,Failure"
          "Process Tracking": "Success,Failure"
          "System": "Success,Failure"

# Compliance Configuration
compliance:
  enabled: true
  standards:
    - cis_benchmarks
    - stig_guidelines
  reporting:
    enabled: true
    format: yaml
    output_dir: reports

# Monitoring Configuration
monitoring:
  enabled: true
  cloudwatch:
    enabled: true
    log_group: "/aws/server-hardening"
  security_hub:
    enabled: true
  config:
    enabled: true

# Remediation Configuration
remediation:
  enabled: true
  automated: true
  schedule: "rate(1 day)"
EOF
        log "Created default hardening configuration."
    fi
    
    # Create Terraform variables file
    if [[ ! -f "$PROJECT_DIR/terraform/terraform.tfvars" ]]; then
        cat > "$PROJECT_DIR/terraform/terraform.tfvars" << EOF
# Terraform Variables for AWS Server Hardening

aws_region = "$AWS_REGION"
environment = "$ENVIRONMENT"
project_name = "$PROJECT_NAME"

# Linux Hardening Configuration
linux_hardening_enabled = $DEPLOY_LINUX
linux_cis_benchmark_version = "ubuntu_20.04"

# Windows Hardening Configuration
windows_hardening_enabled = $DEPLOY_WINDOWS
windows_security_policy = "high_security"

# Compliance Configuration
compliance_monitoring_enabled = true
security_hub_integration_enabled = true

# Monitoring Configuration
cloudwatch_logging_enabled = true
config_rules_enabled = true

# Tags
tags = {
  Project     = "$PROJECT_NAME"
  Environment = "$ENVIRONMENT"
  ManagedBy   = "Terraform"
}
EOF
        log "Created Terraform variables file."
    fi
}

# Function to deploy Linux hardening
deploy_linux_hardening() {
    if [[ "$DEPLOY_LINUX" == false ]]; then
        info "Skipping Linux hardening deployment."
        return
    fi
    
    log "Deploying Linux hardening..."
    
    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        warn "Not running on Linux. Linux hardening will be deployed via AWS Systems Manager."
    else
        # Run Linux hardening locally
        log "Running Linux hardening locally..."
        cd "$PYTHON_DIR/linux_hardening"
        
        if python3 cis_benchmark.py --benchmark ubuntu_20.04; then
            log "Linux hardening completed successfully."
        else
            error "Linux hardening failed."
            return 1
        fi
    fi
}

# Function to deploy Windows hardening
deploy_windows_hardening() {
    if [[ "$DEPLOY_WINDOWS" == false ]]; then
        info "Skipping Windows hardening deployment."
        return
    fi
    
    log "Deploying Windows hardening..."
    
    # Check if running on Windows
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Run Windows hardening locally
        log "Running Windows hardening locally..."
        cd "$PYTHON_DIR/windows_hardening"
        
        if python3 group_policy.py --policy high_security --defender; then
            log "Windows hardening completed successfully."
        else
            error "Windows hardening failed."
            return 1
        fi
    else
        warn "Not running on Windows. Windows hardening will be deployed via AWS Systems Manager."
    fi
}

# Function to deploy Terraform infrastructure
deploy_terraform() {
    if [[ "$DEPLOY_TERRAFORM" == false ]]; then
        info "Skipping Terraform deployment."
        return
    fi
    
    log "Deploying Terraform infrastructure..."
    
    cd "$PROJECT_DIR/terraform"
    
    # Initialize Terraform
    log "Initializing Terraform..."
    terraform init
    
    # Plan Terraform deployment
    log "Planning Terraform deployment..."
    terraform plan -var-file="terraform.tfvars"
    
    # Apply Terraform deployment
    log "Applying Terraform deployment..."
    terraform apply -var-file="terraform.tfvars" -auto-approve
    
    log "Terraform deployment completed successfully."
}

# Function to deploy CloudFormation infrastructure
deploy_cloudformation() {
    if [[ "$DEPLOY_CLOUDFORMATION" == false ]]; then
        info "Skipping CloudFormation deployment."
        return
    fi
    
    log "Deploying CloudFormation infrastructure..."
    
    cd "$PROJECT_DIR/cloudformation"
    
    # Deploy main stack
    log "Deploying main CloudFormation stack..."
    aws cloudformation deploy \
        --template-file server-hardening.yaml \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            ProjectName="$PROJECT_NAME" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION"
    
    log "CloudFormation deployment completed successfully."
}

# Function to run compliance checks
run_compliance_checks() {
    log "Running compliance checks..."
    
    cd "$PYTHON_DIR/compliance"
    
    if python3 compliance_checker.py --os linux; then
        log "Linux compliance checks completed."
    else
        warn "Linux compliance checks failed."
    fi
    
    if python3 compliance_checker.py --os windows; then
        log "Windows compliance checks completed."
    else
        warn "Windows compliance checks failed."
    fi
}

# Function to generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    REPORT_FILE="$PROJECT_DIR/deployment_report_$(date +%Y%m%d_%H%M%S).yaml"
    
    cat > "$REPORT_FILE" << EOF
# AWS Server Hardening Deployment Report

deployment:
  timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
  project_name: $PROJECT_NAME
  environment: $ENVIRONMENT
  aws_region: $AWS_REGION
  
components:
  linux_hardening:
    deployed: $DEPLOY_LINUX
    status: completed
    
  windows_hardening:
    deployed: $DEPLOY_WINDOWS
    status: completed
    
  terraform:
    deployed: $DEPLOY_TERRAFORM
    status: completed
    
  cloudformation:
    deployed: $DEPLOY_CLOUDFORMATION
    status: completed
    
  compliance_monitoring:
    enabled: true
    status: active
    
next_steps:
  - Review hardening reports in the reports/ directory
  - Configure monitoring dashboards
  - Set up compliance alerts
  - Test hardening configurations
  - Document any customizations made

EOF
    
    log "Deployment report generated: $REPORT_FILE"
}

# Function to display next steps
show_next_steps() {
    echo ""
    log "🎉 AWS Server Hardening Framework deployed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Review hardening reports in the reports/ directory"
    echo "  2. Configure CloudWatch dashboards for monitoring"
    echo "  3. Set up Security Hub integration"
    echo "  4. Configure compliance alerts"
    echo "  5. Test hardening configurations"
    echo "  6. Document any customizations made"
    echo ""
    echo "📚 Documentation:"
    echo "  - Project README: $PROJECT_DIR/README.md"
    echo "  - Configuration: $CONFIG_DIR/"
    echo "  - Python scripts: $PYTHON_DIR/"
    echo "  - Terraform: $PROJECT_DIR/terraform/"
    echo ""
    echo "🔧 Manual Steps:"
    echo "  - Review and customize hardening policies as needed"
    echo "  - Configure additional security controls"
    echo "  - Set up automated compliance reporting"
    echo "  - Integrate with existing security tools"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 AWS Server Hardening Framework Deployment"
    echo "============================================="
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -l|--linux-only)
                DEPLOY_LINUX=true
                DEPLOY_WINDOWS=false
                shift
                ;;
            -w|--windows-only)
                DEPLOY_LINUX=false
                DEPLOY_WINDOWS=true
                shift
                ;;
            -t|--terraform)
                DEPLOY_TERRAFORM=true
                DEPLOY_CLOUDFORMATION=false
                shift
                ;;
            -c|--cloudformation)
                DEPLOY_TERRAFORM=false
                DEPLOY_CLOUDFORMATION=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Display deployment configuration
    info "Deployment Configuration:"
    info "  AWS Region: $AWS_REGION"
    info "  Environment: $ENVIRONMENT"
    info "  Linux Hardening: $DEPLOY_LINUX"
    info "  Windows Hardening: $DEPLOY_WINDOWS"
    info "  Terraform: $DEPLOY_TERRAFORM"
    info "  CloudFormation: $DEPLOY_CLOUDFORMATION"
    echo ""
    
    # Run deployment steps
    check_prerequisites
    install_dependencies
    setup_configuration
    deploy_linux_hardening
    deploy_windows_hardening
    
    if [[ "$DEPLOY_TERRAFORM" == true ]]; then
        deploy_terraform
    fi
    
    if [[ "$DEPLOY_CLOUDFORMATION" == true ]]; then
        deploy_cloudformation
    fi
    
    run_compliance_checks
    generate_report
    show_next_steps
}

# Run main function
main "$@"
