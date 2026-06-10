#!/bin/bash

# Deploy infrastructure components for the AWS Audit Framework (Terraform)
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

PROJECT_NAME="aws-audit-framework"
ENVIRONMENT="production"

usage() {
  cat <<EOF
Deploy AWS Audit Framework infrastructure using Terraform

Usage: $0 [-n PROJECT_NAME] [-e ENVIRONMENT]
  -n  Project name (default: aws-audit-framework)
  -e  Environment name (default: production)
EOF
}

while getopts n:e:h flag; do
  case "$flag" in
    n) PROJECT_NAME="$OPTARG" ;;
    e) ENVIRONMENT="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

print_status "Checking prerequisites..."
if ! command -v terraform >/dev/null 2>&1; then
  print_error "Terraform is not installed. Please install it first."
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  print_warning "AWS CLI not found. Continuing, but Terraform may fail if providers need credentials."
fi

cd "$TERRAFORM_DIR"
print_status "Initializing Terraform..."
terraform init || { print_error "Terraform init failed"; exit 1; }

print_status "Planning Terraform changes..."
terraform plan -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" || print_warning "Terraform plan failed; review configuration."

print_status "Applying Terraform changes..."
if terraform apply -auto-approve -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT"; then
  print_success "Terraform deployment completed."
  print_status "Outputs:"
  terraform output || true
else
  print_error "Terraform apply failed."
  exit 1
fi
