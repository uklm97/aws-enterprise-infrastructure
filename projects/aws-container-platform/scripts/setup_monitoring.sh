#!/bin/bash

# AWS Container Platform Monitoring Setup Script
# This script sets up comprehensive monitoring for the Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
HELM_DIR="$PROJECT_ROOT/helm"

# Default values
CLUSTER_NAME=""
NAMESPACE="monitoring"
ENABLE_PROMETHEUS="true"
ENABLE_GRAFANA="true"
ENABLE_ELASTICSEARCH="true"
ENABLE_KIBANA="true"
ENABLE_FLUENTD="true"

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

Setup comprehensive monitoring for Kubernetes cluster

OPTIONS:
    -c, --cluster-name NAME     EKS cluster name (required)
    -n, --namespace NAMESPACE   Kubernetes namespace for monitoring (default: monitoring)
    -p, --no-prometheus         Skip Prometheus installation
    -g, --no-grafana            Skip Grafana installation
    -e, --no-elasticsearch      Skip Elasticsearch installation
    -k, --no-kibana             Skip Kibana installation
    -f, --no-fluentd            Skip Fluentd installation
    -h, --help                  Show this help message

EXAMPLES:
    # Setup all monitoring components
    $0 --cluster-name my-cluster

    # Setup only Prometheus and Grafana
    $0 --cluster-name my-cluster --no-elasticsearch --no-kibana --no-fluentd

    # Setup in custom namespace
    $0 --cluster-name my-cluster --namespace observability
EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
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
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to create namespace
create_namespace() {
    print_status "Creating namespace: $NAMESPACE"
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespace $NAMESPACE created/verified"
}

# Function to setup Prometheus monitoring
setup_prometheus() {
    if [ "$ENABLE_PROMETHEUS" = "false" ]; then
        print_warning "Skipping Prometheus installation"
        return
    fi
    
    print_status "Setting up Prometheus monitoring..."
    
    # Add Prometheus Community Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install Prometheus Operator
    helm upgrade --install prometheus-operator \
        prometheus-community/kube-prometheus-stack \
        --namespace "$NAMESPACE" \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false \
        --wait
    
    print_success "Prometheus monitoring setup completed"
}

# Function to setup Elasticsearch logging
setup_elasticsearch() {
    if [ "$ENABLE_ELASTICSEARCH" = "false" ]; then
        print_warning "Skipping Elasticsearch installation"
        return
    fi
    
    print_status "Setting up Elasticsearch logging..."
    
    # Add Elastic Helm repository
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Install Elasticsearch
    helm upgrade --install elasticsearch \
        elastic/elasticsearch \
        --namespace "$NAMESPACE" \
        --set replicas=3 \
        --set minimumMasterNodes=2 \
        --set resources.requests.cpu=1000m \
        --set resources.requests.memory=2Gi \
        --set resources.limits.cpu=2000m \
        --set resources.limits.memory=4Gi \
        --set volumeClaimTemplate.spec.resources.requests.storage=50Gi \
        --set volumeClaimTemplate.spec.storageClassName=gp2 \
        --wait
    
    print_success "Elasticsearch logging setup completed"
}

# Function to setup Kibana
setup_kibana() {
    if [ "$ENABLE_KIBANA" = "false" ]; then
        print_warning "Skipping Kibana installation"
        return
    fi
    
    print_status "Setting up Kibana..."
    
    # Install Kibana
    helm upgrade --install kibana \
        elastic/kibana \
        --namespace "$NAMESPACE" \
        --set elasticsearchHosts=http://elasticsearch-master:9200 \
        --set resources.requests.cpu=500m \
        --set resources.requests.memory=1Gi \
        --set resources.limits.cpu=1000m \
        --set resources.limits.memory=2Gi \
        --set service.type=LoadBalancer \
        --wait
    
    print_success "Kibana setup completed"
}

# Function to setup Fluentd
setup_fluentd() {
    if [ "$ENABLE_FLUENTD" = "false" ]; then
        print_warning "Skipping Fluentd installation"
        return
    fi
    
    print_status "Setting up Fluentd logging..."
    
    # Create Fluentd ConfigMap
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: $NAMESPACE
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch-master
      port 9200
      index_name kubernetes-logs
      type_name fluentd
      logstash_format true
      logstash_prefix kubernetes
      logstash_dateformat %Y%m%d
      include_tag_key true
      tag_key @log_name
      flush_interval 5s
      max_retry_wait 30s
      disable_retry_limit false
      reload_connections false
      reload_on_failure true
      resurrect_after 60s
      reconnect_on_error true
      reload_connections false
      buffer_type file
      buffer_path /var/log/fluentd-buffers/kubernetes.system.buffer
      buffer_queue_limit 8
      buffer_chunk_limit 2m
      buffer_queue_full_action block
      retry_max_interval 30s
      retry_forever true
      max_retry_wait 30s
      disable_retry_limit false
      reload_connections false
      reload_on_failure true
      resurrect_after 60s
      reconnect_on_error true
      reload_connections false
      buffer_type file
      buffer_path /var/log/fluentd-buffers/kubernetes.system.buffer
      buffer_queue_limit 8
      buffer_chunk_limit 2m
      buffer_queue_full_action block
      retry_max_interval 30s
      retry_forever true
    </match>
EOF
    
    # Create Fluentd DaemonSet
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: $NAMESPACE
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: elasticsearch-master
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        - name: FLUENT_ELASTICSEARCH_SCHEME
          value: http
        - name: FLUENT_ELASTICSEARCH_USER
          value: ""
        - name: FLUENT_ELASTICSEARCH_PASSWORD
          value: ""
        - name: FLUENT_ELASTICSEARCH_INDEX_NAME
          value: kubernetes-logs
        - name: FLUENT_ELASTICSEARCH_TYPE_NAME
          value: fluentd
        - name: FLUENT_ELASTICSEARCH_LOGSTASH_FORMAT
          value: "true"
        - name: FLUENT_ELASTICSEARCH_LOGSTASH_PREFIX
          value: kubernetes
        - name: FLUENT_ELASTICSEARCH_LOGSTASH_DATE_FORMAT
          value: "%Y%m%d"
        - name: FLUENT_ELASTICSEARCH_INCLUDE_TAG_KEY
          value: "true"
        - name: FLUENT_ELASTICSEARCH_TAG_KEY
          value: "@log_name"
        - name: FLUENT_ELASTICSEARCH_FLUSH_INTERVAL
          value: "5s"
        - name: FLUENT_ELASTICSEARCH_MAX_RETRY_WAIT
          value: "30s"
        - name: FLUENT_ELASTICSEARCH_DISABLE_RETRY_LIMIT
          value: "false"
        - name: FLUENT_ELASTICSEARCH_RELOAD_CONNECTIONS
          value: "false"
        - name: FLUENT_ELASTICSEARCH_RELOAD_ON_FAILURE
          value: "true"
        - name: FLUENT_ELASTICSEARCH_RESURRECT_AFTER
          value: "60s"
        - name: FLUENT_ELASTICSEARCH_RECONNECT_ON_ERROR
          value: "true"
        - name: FLUENT_ELASTICSEARCH_RELOAD_CONNECTIONS
          value: "false"
        - name: FLUENT_ELASTICSEARCH_BUFFER_TYPE
          value: file
        - name: FLUENT_ELASTICSEARCH_BUFFER_PATH
          value: /var/log/fluentd-buffers/kubernetes.system.buffer
        - name: FLUENT_ELASTICSEARCH_BUFFER_QUEUE_LIMIT
          value: "8"
        - name: FLUENT_ELASTICSEARCH_BUFFER_CHUNK_LIMIT
          value: 2m
        - name: FLUENT_ELASTICSEARCH_BUFFER_QUEUE_FULL_ACTION
          value: block
        - name: FLUENT_ELASTICSEARCH_RETRY_MAX_INTERVAL
          value: "30s"
        - name: FLUENT_ELASTICSEARCH_RETRY_FOREVER
          value: "true"
        - name: FLUENT_ELASTICSEARCH_MAX_RETRY_WAIT
          value: "30s"
        - name: FLUENT_ELASTICSEARCH_DISABLE_RETRY_LIMIT
          value: "false"
        - name: FLUENT_ELASTICSEARCH_RELOAD_CONNECTIONS
          value: "false"
        - name: FLUENT_ELASTICSEARCH_RELOAD_ON_FAILURE
          value: "true"
        - name: FLUENT_ELASTICSEARCH_RESURRECT_AFTER
          value: "60s"
        - name: FLUENT_ELASTICSEARCH_RECONNECT_ON_ERROR
          value: "true"
        - name: FLUENT_ELASTICSEARCH_RELOAD_CONNECTIONS
          value: "false"
        - name: FLUENT_ELASTICSEARCH_BUFFER_TYPE
          value: file
        - name: FLUENT_ELASTICSEARCH_BUFFER_PATH
          value: /var/log/fluentd-buffers/kubernetes.system.buffer
        - name: FLUENT_ELASTICSEARCH_BUFFER_QUEUE_LIMIT
          value: "8"
        - name: FLUENT_ELASTICSEARCH_BUFFER_CHUNK_LIMIT
          value: 2m
        - name: FLUENT_ELASTICSEARCH_BUFFER_QUEUE_FULL_ACTION
          value: block
        - name: FLUENT_ELASTICSEARCH_RETRY_MAX_INTERVAL
          value: "30s"
        - name: FLUENT_ELASTICSEARCH_RETRY_FOREVER
          value: "true"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluentd-config
          mountPath: /fluentd/etc
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluentd-config
        configMap:
          name: fluentd-config
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
EOF
    
    print_success "Fluentd logging setup completed"
}

# Function to setup ingress for monitoring services
setup_ingress() {
    print_status "Setting up ingress for monitoring services..."
    
    # Check if NGINX Ingress Controller is installed
    if ! kubectl get pods -n ingress-nginx &> /dev/null; then
        print_warning "NGINX Ingress Controller not found. Installing..."
        
        # Install NGINX Ingress Controller
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml
        
        # Wait for ingress controller to be ready
        kubectl wait --namespace ingress-nginx \
            --for=condition=ready pod \
            --selector=app.kubernetes.io/component=controller \
            --timeout=300s
    fi
    
    # Create ingress for Grafana
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: grafana.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus-operator-grafana
            port:
              number: 80
EOF
    
    # Create ingress for Kibana
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kibana-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: kibana.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kibana-kibana
            port:
              number: 5601
EOF
    
    print_success "Ingress setup completed"
}

# Function to display monitoring information
display_monitoring_info() {
    print_status "Monitoring setup completed!"
    echo ""
    echo "=== Monitoring Services ==="
    echo ""
    
    # Get service information
    echo "Services in $NAMESPACE namespace:"
    kubectl get svc -n "$NAMESPACE"
    echo ""
    
    # Get pod information
    echo "Pods in $NAMESPACE namespace:"
    kubectl get pods -n "$NAMESPACE"
    echo ""
    
    # Get ingress information
    echo "Ingress resources:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""
    
    echo "=== Access Information ==="
    echo ""
    echo "Grafana:"
    echo "  URL: http://grafana.example.com"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo "Kibana:"
    echo "  URL: http://kibana.example.com"
    echo ""
    echo "Prometheus:"
    echo "  Port-forward: kubectl port-forward -n $NAMESPACE svc/prometheus-operator-prometheus 9090:9090"
    echo "  URL: http://localhost:9090"
    echo ""
    echo "Alertmanager:"
    echo "  Port-forward: kubectl port-forward -n $NAMESPACE svc/prometheus-operator-alertmanager 9093:9093"
    echo "  URL: http://localhost:9093"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Update your DNS to point grafana.example.com and kibana.example.com to your ingress controller"
    echo "2. Access Grafana and import dashboards for Kubernetes monitoring"
    echo "3. Configure alerts in Alertmanager"
    echo "4. Set up log shipping from your applications to Elasticsearch"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -p|--no-prometheus)
            ENABLE_PROMETHEUS="false"
            shift
            ;;
        -g|--no-grafana)
            ENABLE_GRAFANA="false"
            shift
            ;;
        -e|--no-elasticsearch)
            ENABLE_ELASTICSEARCH="false"
            shift
            ;;
        -k|--no-kibana)
            ENABLE_KIBANA="false"
            shift
            ;;
        -f|--no-fluentd)
            ENABLE_FLUENTD="false"
            shift
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

# Validate required parameters
if [ -z "$CLUSTER_NAME" ]; then
    print_error "Cluster name is required. Use --cluster-name option."
    show_usage
    exit 1
fi

# Main execution
main() {
    print_status "Starting monitoring setup for cluster: $CLUSTER_NAME"
    
    # Check prerequisites
    check_prerequisites
    
    # Create namespace
    create_namespace
    
    # Setup monitoring components
    setup_prometheus
    setup_elasticsearch
    setup_kibana
    setup_fluentd
    
    # Setup ingress
    setup_ingress
    
    # Display information
    display_monitoring_info
    
    print_success "Monitoring setup completed successfully!"
}

# Run main function
main "$@"