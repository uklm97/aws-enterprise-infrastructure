#!/bin/bash

# AWS Container & Kubernetes Platform Deployment Script
# This script deploys the complete container platform using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AWS_REGION="us-east-1"
PROJECT_NAME="aws-container-platform"
ENVIRONMENT="production"
CLUSTER_NAME="aws-container-platform"
KUBERNETES_VERSION="1.27"
VPC_CIDR="10.0.0.0/16"
NODE_INSTANCE_TYPES="t3.medium"
NODE_MIN_SIZE="1"
NODE_MAX_SIZE="10"
NODE_DESIRED_SIZE="3"
SPOT_ENABLED="false"
SPOT_MIN_SIZE="0"
SPOT_MAX_SIZE="5"
SPOT_DESIRED_SIZE="0"
INSTALL_ALB_CONTROLLER="true"
INSTALL_CLUSTER_AUTOSCALER="true"
INSTALL_METRICS_SERVER="true"
CREATE_ALARMS="true"
LOG_RETENTION_DAYS="30"

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

Deploy AWS Container & Kubernetes Platform

OPTIONS:
    -r, --region REGION              AWS region [default: us-east-1]
    -p, --project-name NAME          Project name [default: aws-container-platform]
    -e, --environment ENV            Environment [default: production]
    -c, --cluster-name NAME          Cluster name [default: aws-container-platform]
    -k, --kubernetes-version VER     Kubernetes version [default: 1.27]
    --vpc-cidr CIDR                  VPC CIDR block [default: 10.0.0.0/16]
    --node-instance-types TYPES      Node instance types [default: t3.medium]
    --node-min-size SIZE             Minimum node count [default: 1]
    --node-max-size SIZE             Maximum node count [default: 10]
    --node-desired-size SIZE         Desired node count [default: 3]
    --enable-spot                    Enable spot instances
    --spot-min-size SIZE             Minimum spot node count [default: 0]
    --spot-max-size SIZE             Maximum spot node count [default: 5]
    --spot-desired-size SIZE         Desired spot node count [default: 0]
    --no-alb-controller              Don't install AWS Load Balancer Controller
    --no-cluster-autoscaler          Don't install Cluster Autoscaler
    --no-metrics-server              Don't install Metrics Server
    --no-alarms                      Don't create CloudWatch alarms
    --log-retention-days DAYS        CloudWatch log retention days [default: 30]
    --destroy                        Destroy the platform
    -h, --help                       Show this help message

EXAMPLES:
    # Deploy with default settings
    $0

    # Deploy with custom settings
    $0 --region us-west-2 --cluster-name my-cluster --node-desired-size 5

    # Deploy with spot instances
    $0 --enable-spot --spot-desired-size 2

    # Destroy the platform
    $0 --destroy

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
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed. Please install it first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to validate parameters
validate_parameters() {
    print_status "Validating parameters..."
    
    # Validate AWS region
    if ! aws ec2 describe-regions --region-names "$AWS_REGION" &> /dev/null; then
        print_error "Invalid AWS region: $AWS_REGION"
        exit 1
    fi
    
    # Validate Kubernetes version
    if [[ ! "$KUBERNETES_VERSION" =~ ^[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid Kubernetes version format: $KUBERNETES_VERSION"
        exit 1
    fi
    
    # Validate VPC CIDR
    if [[ ! "$VPC_CIDR" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]]; then
        print_error "Invalid VPC CIDR format: $VPC_CIDR"
        exit 1
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
cluster_name = "$CLUSTER_NAME"
kubernetes_version = "$KUBERNETES_VERSION"
vpc_cidr = "$VPC_CIDR"
node_instance_types = ["$NODE_INSTANCE_TYPES"]
node_min_size = $NODE_MIN_SIZE
node_max_size = $NODE_MAX_SIZE
node_desired_size = $NODE_DESIRED_SIZE
spot_min_size = $SPOT_MIN_SIZE
spot_max_size = $SPOT_MAX_SIZE
spot_desired_size = $SPOT_DESIRED_SIZE
install_aws_load_balancer_controller = $INSTALL_ALB_CONTROLLER
install_cluster_autoscaler = $INSTALL_CLUSTER_AUTOSCALER
install_metrics_server = $INSTALL_METRICS_SERVER
create_alarms = $CREATE_ALARMS
log_retention_days = $LOG_RETENTION_DAYS
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

# Function to configure kubectl
configure_kubectl() {
    print_status "Configuring kubectl..."
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
    
    # Verify cluster access
    if kubectl get nodes &> /dev/null; then
        print_success "kubectl configured successfully"
    else
        print_error "Failed to configure kubectl"
        exit 1
    fi
}

# Function to deploy Kubernetes resources
deploy_kubernetes_resources() {
    print_status "Deploying Kubernetes resources..."
    
    # Create namespaces
    print_status "Creating namespaces..."
    kubectl apply -f kubernetes/namespaces/
    
    # Deploy sample application
    print_status "Deploying sample application..."
    kubectl apply -f kubernetes/deployments/
    
    # Wait for deployments to be ready
    print_status "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/sample-app
    
    print_success "Kubernetes resources deployed successfully"
}

# Function to install Helm charts
install_helm_charts() {
    print_status "Installing Helm charts..."
    
    # Add Helm repositories
    print_status "Adding Helm repositories..."
    helm repo add stable https://charts.helm.sh/stable
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Install monitoring stack
    print_status "Installing monitoring stack..."
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.retention=30d \
        --wait
    
    # Install logging stack
    print_status "Installing logging stack..."
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace logging \
        --create-namespace \
        --set replicas=1 \
        --set resources.requests.memory=1Gi \
        --wait
    
    helm upgrade --install kibana elastic/kibana \
        --namespace logging \
        --create-namespace \
        --set elasticsearchHosts=http://elasticsearch-master:9200 \
        --wait
    
    print_success "Helm charts installed successfully"
}

# Function to show cluster information
show_cluster_info() {
    print_status "Cluster Information:"
    echo "  Cluster Name: $CLUSTER_NAME"
    echo "  Region: $AWS_REGION"
    echo "  Kubernetes Version: $KUBERNETES_VERSION"
    echo ""
    
    print_status "Cluster Status:"
    kubectl get nodes
    echo ""
    
    print_status "Pods Status:"
    kubectl get pods --all-namespaces
    echo ""
    
    print_status "Services Status:"
    kubectl get services --all-namespaces
    echo ""
    
    print_status "Ingress Status:"
    kubectl get ingress --all-namespaces
    echo ""
}

# Function to cleanup resources
cleanup() {
    print_status "Cleaning up resources..."
    
    cd terraform
    terraform destroy -auto-approve
    cd ..
    
    print_success "Cleanup completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
        -c|--cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -k|--kubernetes-version)
            KUBERNETES_VERSION="$2"
            shift 2
            ;;
        --vpc-cidr)
            VPC_CIDR="$2"
            shift 2
            ;;
        --node-instance-types)
            NODE_INSTANCE_TYPES="$2"
            shift 2
            ;;
        --node-min-size)
            NODE_MIN_SIZE="$2"
            shift 2
            ;;
        --node-max-size)
            NODE_MAX_SIZE="$2"
            shift 2
            ;;
        --node-desired-size)
            NODE_DESIRED_SIZE="$2"
            shift 2
            ;;
        --enable-spot)
            SPOT_ENABLED="true"
            shift
            ;;
        --spot-min-size)
            SPOT_MIN_SIZE="$2"
            shift 2
            ;;
        --spot-max-size)
            SPOT_MAX_SIZE="$2"
            shift 2
            ;;
        --spot-desired-size)
            SPOT_DESIRED_SIZE="$2"
            shift 2
            ;;
        --no-alb-controller)
            INSTALL_ALB_CONTROLLER="false"
            shift
            ;;
        --no-cluster-autoscaler)
            INSTALL_CLUSTER_AUTOSCALER="false"
            shift
            ;;
        --no-metrics-server)
            INSTALL_METRICS_SERVER="false"
            shift
            ;;
        --no-alarms)
            CREATE_ALARMS="false"
            shift
            ;;
        --log-retention-days)
            LOG_RETENTION_DAYS="$2"
            shift 2
            ;;
        --destroy)
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
    print_status "Starting AWS Container & Kubernetes Platform deployment..."
    print_status "Cluster name: $CLUSTER_NAME"
    print_status "AWS region: $AWS_REGION"
    print_status "Kubernetes version: $KUBERNETES_VERSION"
    print_status "Environment: $ENVIRONMENT"
    
    check_prerequisites
    validate_parameters
    deploy_terraform
    configure_kubectl
    deploy_kubernetes_resources
    install_helm_charts
    show_cluster_info
    
    print_success "AWS Container & Kubernetes Platform deployment completed successfully!"
    print_status "You can now use the deployed container platform for your applications."
    print_status "Access the cluster with: kubectl get nodes"
}

# Run main function
main "$@"