#!/bin/bash

# AWS Cloud Environment Infrastructure Audit Framework
# This script provides a unified interface to run comprehensive AWS infrastructure audits
# using both Python (boto3) and Terraform implementations.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="$PROJECT_ROOT/python"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
REPORTS_DIR="$PROJECT_ROOT/reports"
CONFIG_DIR="$PROJECT_ROOT/config"

# Default values
AUDIT_TYPE="comprehensive"
IMPLEMENTATION="python"
OUTPUT_FORMAT="json"
VERBOSE=false
DEBUG=false
CONFIG_FILE=""
REGION=""
PROFILE=""

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
    cat << EOF
AWS Cloud Environment Infrastructure Audit Framework

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --type TYPE           Audit type (comprehensive|security|cost|performance|compliance|infrastructure)
    -i, --implementation IMP  Implementation (python|terraform|both)
    -o, --output FORMAT       Output format (json|html|pdf|csv)
    -c, --config FILE         Configuration file path
    -r, --region REGION       AWS region
    -p, --profile PROFILE     AWS profile
    -v, --verbose             Enable verbose output
    -d, --debug               Enable debug output
    -h, --help                Display this help message

EXAMPLES:
    # Run comprehensive audit with Python
    $0 --type comprehensive --implementation python

    # Run security audit with Terraform
    $0 --type security --implementation terraform

    # Run both implementations
    $0 --type comprehensive --implementation both

    # Run with custom configuration
    $0 --config custom_config.yaml --region us-west-2

AUDIT TYPES:
    comprehensive    - Run all audit modules (default)
    security         - Security audit only (IAM, Security Groups, VPC, Encryption)
    cost             - Cost audit only (utilization, optimization, budget)
    performance      - Performance audit only (CloudWatch metrics, bottlenecks)
    compliance       - Compliance audit only (Config rules, CIS benchmarks)
    infrastructure   - Infrastructure audit only (inventory, drift, best practices)

IMPLEMENTATIONS:
    python          - Use Python boto3 implementation (default)
    terraform       - Use Terraform implementation
    both            - Use both implementations

OUTPUT FORMATS:
    json            - JSON format (default)
    html            - HTML format
    pdf             - PDF format
    csv             - CSV format

EOF
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
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Python (for Python implementation)
    if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
        if ! command -v python3 &> /dev/null; then
            print_error "Python 3 is not installed. Please install it first."
            exit 1
        fi
        
        # Check Python version
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
            print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    fi
    
    # Check Terraform (for Terraform implementation)
    if [[ "$IMPLEMENTATION" == "terraform" || "$IMPLEMENTATION" == "both" ]]; then
        if ! command -v terraform &> /dev/null; then
            print_error "Terraform is not installed. Please install it first."
            exit 1
        fi
        
        # Check Terraform version
        TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
        if [[ $(echo "$TERRAFORM_VERSION >= 1.0" | bc -l) -eq 0 ]]; then
            print_error "Terraform 1.0 or higher is required. Current version: $TERRAFORM_VERSION"
            exit 1
        fi
    fi
    
    # Check jq
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some features may not work properly."
    fi
    
    print_success "Prerequisites check completed"
}

# Function to validate configuration
validate_config() {
    print_status "Validating configuration..."
    
    if [[ -n "$CONFIG_FILE" && ! -f "$CONFIG_FILE" ]]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    if [[ -n "$REGION" ]]; then
        # Validate AWS region
        if ! aws ec2 describe-regions --region "$REGION" &> /dev/null; then
            print_error "Invalid AWS region: $REGION"
            exit 1
        fi
    fi
    
    print_success "Configuration validation completed"
}

# Function to run Python audit
run_python_audit() {
    print_status "Running Python audit implementation..."
    
    cd "$PYTHON_DIR"
    
    # Install dependencies if requirements.txt exists
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing Python dependencies..."
        pip3 install -r requirements.txt
    fi
    
    # Build command
    CMD="python3 audit_framework.py"
    
    # Add audit type
    case "$AUDIT_TYPE" in
        "comprehensive")
            CMD="$CMD --comprehensive"
            ;;
        "security")
            CMD="$CMD --security"
            ;;
        "cost")
            CMD="$CMD --cost"
            ;;
        "performance")
            CMD="$CMD --performance"
            ;;
        "compliance")
            CMD="$CMD --compliance"
            ;;
        "infrastructure")
            CMD="$CMD --infrastructure"
            ;;
    esac
    
    # Add configuration file
    if [[ -n "$CONFIG_FILE" ]]; then
        CMD="$CMD --config $CONFIG_FILE"
    fi
    
    # Add output format
    CMD="$CMD --output-format $OUTPUT_FORMAT"
    
    # Add region
    if [[ -n "$REGION" ]]; then
        CMD="$CMD --region $REGION"
    fi
    
    # Add profile
    if [[ -n "$PROFILE" ]]; then
        export AWS_PROFILE="$PROFILE"
    fi
    
    # Add verbosity
    if [[ "$VERBOSE" == true ]]; then
        CMD="$CMD --verbose"
    fi
    
    if [[ "$DEBUG" == true ]]; then
        CMD="$CMD --debug"
    fi
    
    print_status "Executing: $CMD"
    eval "$CMD"
    
    if [[ $? -eq 0 ]]; then
        print_success "Python audit completed successfully"
    else
        print_error "Python audit failed"
        return 1
    fi
}

# Function to run Terraform audit
run_terraform_audit() {
    print_status "Running Terraform audit implementation..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan Terraform changes
    print_status "Planning Terraform changes..."
    terraform plan -var="project_name=aws-audit-framework" -var="environment=production"
    
    # Apply Terraform changes
    print_status "Applying Terraform changes..."
    terraform apply -auto-approve -var="project_name=aws-audit-framework" -var="environment=production"
    
    if [[ $? -eq 0 ]]; then
        print_success "Terraform audit infrastructure deployed successfully"
        
        # Get outputs
        print_status "Getting Terraform outputs..."
        terraform output -json > "$REPORTS_DIR/terraform_outputs.json"
        
        # Run audit using deployed infrastructure
        print_status "Running audit using deployed infrastructure..."
        # This would typically involve invoking the deployed Lambda function
        # or using the deployed AWS Config rules and CloudWatch dashboards
    else
        print_error "Terraform audit failed"
        return 1
    fi
}

# Function to generate summary report
generate_summary_report() {
    print_status "Generating summary report..."
    
    # Create reports directory if it doesn't exist
    mkdir -p "$REPORTS_DIR"
    
    # Generate summary
    cat > "$REPORTS_DIR/audit_summary.md" << EOF
# AWS Infrastructure Audit Summary

**Audit Date:** $(date)
**Audit Type:** $AUDIT_TYPE
**Implementation:** $IMPLEMENTATION
**Output Format:** $OUTPUT_FORMAT

## Configuration
- **AWS Region:** ${REGION:-$(aws configure get region)}
- **AWS Profile:** ${PROFILE:-default}
- **Config File:** ${CONFIG_FILE:-default}

## Audit Results

### Python Implementation
EOF
    
    if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
        if [[ -f "$PYTHON_DIR/reports/audit_results.json" ]]; then
            echo "- ✅ Python audit completed successfully" >> "$REPORTS_DIR/audit_summary.md"
            echo "- 📊 Results available in: $PYTHON_DIR/reports/" >> "$REPORTS_DIR/audit_summary.md"
        else
            echo "- ❌ Python audit failed or no results found" >> "$REPORTS_DIR/audit_summary.md"
        fi
    fi
    
    cat >> "$REPORTS_DIR/audit_summary.md" << EOF

### Terraform Implementation
EOF
    
    if [[ "$IMPLEMENTATION" == "terraform" || "$IMPLEMENTATION" == "both" ]]; then
        if [[ -f "$REPORTS_DIR/terraform_outputs.json" ]]; then
            echo "- ✅ Terraform infrastructure deployed successfully" >> "$REPORTS_DIR/audit_summary.md"
            echo "- 📊 Infrastructure outputs available in: $REPORTS_DIR/terraform_outputs.json" >> "$REPORTS_DIR/audit_summary.md"
        else
            echo "- ❌ Terraform deployment failed or no outputs found" >> "$REPORTS_DIR/audit_summary.md"
        fi
    fi
    
    cat >> "$REPORTS_DIR/audit_summary.md" << EOF

## Next Steps
1. Review the generated reports
2. Address any critical findings
3. Implement recommended remediations
4. Schedule regular audits

## Files Generated
- Audit Summary: $REPORTS_DIR/audit_summary.md
- Python Reports: $PYTHON_DIR/reports/
- Terraform Outputs: $REPORTS_DIR/terraform_outputs.json

EOF
    
    print_success "Summary report generated: $REPORTS_DIR/audit_summary.md"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Reset AWS profile if it was set
    if [[ -n "$PROFILE" ]]; then
        unset AWS_PROFILE
    fi
    
    print_success "Cleanup completed"
}

# Function to handle script exit
exit_handler() {
    cleanup
    if [[ $? -eq 0 ]]; then
        print_success "Audit completed successfully"
    else
        print_error "Audit failed"
    fi
}

# Set up exit handler
trap exit_handler EXIT

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            AUDIT_TYPE="$2"
            shift 2
            ;;
        -i|--implementation)
            IMPLEMENTATION="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
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

# Validate audit type
case "$AUDIT_TYPE" in
    "comprehensive"|"security"|"cost"|"performance"|"compliance"|"infrastructure")
        ;;
    *)
        print_error "Invalid audit type: $AUDIT_TYPE"
        usage
        exit 1
        ;;
esac

# Validate implementation
case "$IMPLEMENTATION" in
    "python"|"terraform"|"both")
        ;;
    *)
        print_error "Invalid implementation: $IMPLEMENTATION"
        usage
        exit 1
        ;;
esac

# Validate output format
case "$OUTPUT_FORMAT" in
    "json"|"html"|"pdf"|"csv")
        ;;
    *)
        print_error "Invalid output format: $OUTPUT_FORMAT"
        usage
        exit 1
        ;;
esac

# Main execution
main() {
    print_status "Starting AWS Infrastructure Audit Framework"
    print_status "Audit Type: $AUDIT_TYPE"
    print_status "Implementation: $IMPLEMENTATION"
    print_status "Output Format: $OUTPUT_FORMAT"
    
    # Check prerequisites
    check_prerequisites
    
    # Validate configuration
    validate_config
    
    # Run audits based on implementation
    if [[ "$IMPLEMENTATION" == "python" || "$IMPLEMENTATION" == "both" ]]; then
        run_python_audit
    fi
    
    if [[ "$IMPLEMENTATION" == "terraform" || "$IMPLEMENTATION" == "both" ]]; then
        run_terraform_audit
    fi
    
    # Generate summary report
    generate_summary_report
    
    print_success "Audit framework execution completed"
}

# Run main function
main "$@"
