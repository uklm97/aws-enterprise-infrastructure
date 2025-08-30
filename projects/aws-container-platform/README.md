# AWS Container & Kubernetes Platform

A comprehensive AWS container and Kubernetes platform that provides enterprise-grade container orchestration, EKS cluster management, containerized application deployment, and DevOps automation. This project implements modern containerization practices with security, scalability, and operational excellence.

## 🎯 Overview

This project provides a complete container and Kubernetes solution including:

- **EKS Cluster Management** - Production-ready Kubernetes clusters with auto-scaling
- **Container Orchestration** - Advanced container deployment and management
- **Service Mesh** - Istio-based service mesh for microservices
- **CI/CD Integration** - Automated container build and deployment pipelines
- **Monitoring & Observability** - Comprehensive container monitoring and logging
- **Security & Compliance** - Container security scanning and compliance
- **Multi-Environment Support** - Dev, staging, and production environments

## 🏗️ Architecture

### Container Platform Components
```
AWS Container & Kubernetes Platform
├── EKS Clusters
│   ├── Production Cluster
│   ├── Staging Cluster
│   └── Development Cluster
├── Container Orchestration
│   ├── Kubernetes Resources
│   ├── Helm Charts
│   ├── Operators
│   └── Custom Controllers
├── Service Mesh
│   ├── Istio Control Plane
│   ├── Service Discovery
│   ├── Traffic Management
│   └── Security Policies
├── CI/CD Pipeline
│   ├── Container Registry
│   ├── Build Automation
│   ├── Deployment Automation
│   └── Rollback Mechanisms
├── Monitoring & Observability
│   ├── Prometheus & Grafana
│   ├── ELK Stack
│   ├── Distributed Tracing
│   └── Alerting
└── Security & Compliance
    ├── Container Scanning
    ├── Image Signing
    ├── Network Policies
    └── RBAC Management
```

## 📁 Project Structure

```
aws-container-platform/
├── README.md                           # This documentation
├── python/                             # Python automation scripts
│   ├── eks_management/                 # EKS cluster management
│   │   ├── cluster_manager.py         # EKS cluster automation
│   │   ├── node_group_manager.py      # Node group management
│   │   └── addon_manager.py           # EKS addon management
│   ├── container_orchestration/        # Container orchestration
│   │   ├── kubernetes_manager.py      # Kubernetes resource management
│   │   ├── helm_manager.py            # Helm chart management
│   │   └── operator_manager.py        # Kubernetes operator management
│   ├── service_mesh/                   # Service mesh management
│   │   ├── istio_manager.py           # Istio service mesh
│   │   ├── traffic_manager.py         # Traffic management
│   │   └── security_policies.py       # Security policies
│   ├── cicd/                          # CI/CD automation
│   │   ├── pipeline_manager.py        # CI/CD pipeline management
│   │   ├── build_automation.py        # Build automation
│   │   └── deployment_manager.py      # Deployment automation
│   ├── monitoring/                     # Monitoring and observability
│   │   ├── prometheus_manager.py      # Prometheus monitoring
│   │   ├── grafana_manager.py         # Grafana dashboards
│   │   └── alerting_manager.py        # Alerting automation
│   ├── security/                       # Security and compliance
│   │   ├── container_scanner.py       # Container security scanning
│   │   ├── image_signing.py           # Image signing automation
│   │   └── compliance_checker.py      # Compliance validation
│   └── utils/                         # Utility functions
│       ├── kubectl_wrapper.py         # Kubectl wrapper
│       ├── docker_wrapper.py          # Docker wrapper
│       └── helm_wrapper.py            # Helm wrapper
├── terraform/                          # Terraform infrastructure
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Terraform variables
│   ├── outputs.tf                     # Terraform outputs
│   ├── modules/                       # Terraform modules
│   │   ├── eks_cluster/               # EKS cluster module
│   │   ├── node_groups/               # Node groups module
│   │   ├── addons/                    # EKS addons module
│   │   ├── service_mesh/              # Service mesh module
│   │   ├── monitoring/                # Monitoring module
│   │   └── security/                  # Security module
│   └── examples/                      # Example configurations
├── kubernetes/                         # Kubernetes manifests
│   ├── namespaces/                    # Namespace definitions
│   ├── deployments/                   # Deployment manifests
│   ├── services/                      # Service manifests
│   ├── ingress/                       # Ingress configurations
│   ├── configmaps/                    # ConfigMap definitions
│   ├── secrets/                       # Secret definitions
│   ├── storage/                       # Storage configurations
│   └── rbac/                          # RBAC configurations
├── helm/                              # Helm charts
│   ├── applications/                  # Application charts
│   ├── infrastructure/                # Infrastructure charts
│   ├── monitoring/                    # Monitoring charts
│   └── security/                      # Security charts
├── docker/                            # Docker configurations
│   ├── Dockerfiles/                   # Dockerfile templates
│   ├── docker-compose/                # Docker Compose files
│   └── build-scripts/                 # Build scripts
├── cicd/                              # CI/CD configurations
│   ├── github-actions/                # GitHub Actions workflows
│   ├── jenkins/                       # Jenkins pipelines
│   ├── gitlab-ci/                     # GitLab CI/CD
│   └── argocd/                        # ArgoCD configurations
├── monitoring/                        # Monitoring configurations
│   ├── prometheus/                    # Prometheus configurations
│   ├── grafana/                       # Grafana dashboards
│   ├── alertmanager/                  # AlertManager configurations
│   └── jaeger/                        # Distributed tracing
├── security/                          # Security configurations
│   ├── policies/                      # Security policies
│   ├── scanning/                      # Security scanning
│   ├── compliance/                    # Compliance configurations
│   └── certificates/                  # SSL/TLS certificates
├── config/                            # Configuration files
│   ├── platform_config.yaml           # Platform configuration
│   ├── cluster_config.yaml            # Cluster configuration
│   ├── monitoring_config.yaml         # Monitoring configuration
│   └── security_config.yaml           # Security configuration
├── scripts/                           # Deployment and utility scripts
│   ├── deploy_platform.sh             # Deploy container platform
│   ├── setup_cluster.sh               # Setup EKS cluster
│   ├── deploy_applications.sh         # Deploy applications
│   └── monitoring_setup.sh            # Setup monitoring
├── dashboards/                        # Grafana dashboards
│   ├── kubernetes_dashboard.json      # Kubernetes dashboard
│   ├── application_dashboard.json     # Application dashboard
│   ├── infrastructure_dashboard.json  # Infrastructure dashboard
│   └── security_dashboard.json        # Security dashboard
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
1. **AWS CLI** installed and configured
2. **kubectl** installed and configured
3. **helm** installed
4. **docker** installed
5. **Python 3.8+** for automation scripts
6. **Terraform** (for Terraform implementation)
7. **AWS Permissions** - EKS, EC2, IAM, VPC permissions

### Installation

#### 1. Clone and Setup
```bash
cd projects/aws-container-platform
pip install -r requirements.txt
```

#### 2. Configure Platform
```bash
cp config/platform_config.yaml.example config/platform_config.yaml
# Edit configuration with your requirements
```

#### 3. Deploy Infrastructure
```bash
# Using Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Using scripts
./scripts/deploy_platform.sh
```

#### 4. Setup EKS Cluster
```bash
./scripts/setup_cluster.sh
```

#### 5. Deploy Applications
```bash
./scripts/deploy_applications.sh
```

## 🔧 Core Features

### 1. EKS Cluster Management

#### Production-Ready Clusters
```python
# Automated EKS cluster management
- Multi-AZ cluster deployment
- Auto-scaling node groups
- Spot instance integration
- Cluster upgrades and maintenance
- Backup and disaster recovery
```

#### Node Group Management
```python
# Intelligent node group management
- Auto-scaling node groups
- Spot and on-demand instances
- GPU-enabled node groups
- Windows node groups
- Custom AMI support
```

### 2. Container Orchestration

#### Kubernetes Resources
```python
# Comprehensive Kubernetes management
- Deployment automation
- Service mesh integration
- Ingress controller setup
- Storage class management
- RBAC configuration
```

#### Helm Chart Management
```python
# Advanced Helm chart management
- Custom chart development
- Chart repository management
- Automated chart deployment
- Chart versioning and rollback
- Dependency management
```

### 3. Service Mesh (Istio)

#### Traffic Management
```python
# Advanced traffic management
- Load balancing strategies
- Circuit breaker patterns
- Retry and timeout policies
- Traffic splitting and routing
- Canary deployments
```

#### Security Policies
```python
# Service mesh security
- mTLS encryption
- Authorization policies
- Certificate management
- Security context validation
- Network policies
```

### 4. CI/CD Integration

#### Container Registry
```python
# Container registry management
- ECR repository automation
- Image scanning and signing
- Image lifecycle management
- Cross-region replication
- Access control management
```

#### Pipeline Automation
```python
# Automated CI/CD pipelines
- Multi-stage build pipelines
- Automated testing
- Security scanning
- Deployment automation
- Rollback mechanisms
```

### 5. Monitoring & Observability

#### Prometheus & Grafana
```python
# Comprehensive monitoring
- Custom metrics collection
- Alert rule management
- Dashboard automation
- Data retention policies
- High availability setup
```

#### Distributed Tracing
```python
# Application tracing
- Jaeger integration
- Trace sampling
- Performance analysis
- Error tracking
- Service dependency mapping
```

### 6. Security & Compliance

#### Container Security
```python
# Container security scanning
- Vulnerability scanning
- Image signing
- Runtime security
- Compliance checking
- Security policy enforcement
```

#### Network Security
```python
# Network security policies
- Network policies
- Pod security policies
- Service mesh security
- Encryption at rest and in transit
- Access control lists
```

## 🛠️ Implementation Examples

### Python Implementation

#### EKS Cluster Manager
```python
# python/eks_management/cluster_manager.py
import boto3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import subprocess

class EKSClusterManager:
    """
    AWS EKS Cluster Manager for automated cluster management.
    """
    
    def __init__(self):
        self.eks_client = boto3.client('eks')
        self.ec2_client = boto3.client('ec2')
        self.iam_client = boto3.client('iam')
        
    def create_cluster(self, cluster_name: str, region: str, version: str = '1.27'):
        """Create EKS cluster."""
        try:
            # Create cluster
            response = self.eks_client.create_cluster(
                name=cluster_name,
                version=version,
                roleArn=self._get_cluster_role_arn(),
                resourcesVpcConfig={
                    'subnetIds': self._get_subnet_ids(),
                    'securityGroupIds': self._get_security_group_ids(),
                    'endpointPublicAccess': True,
                    'endpointPrivateAccess': True
                },
                logging={
                    'clusterLogging': [
                        {
                            'types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler'],
                            'enabled': True
                        }
                    ]
                },
                tags={
                    'Project': 'aws-container-platform',
                    'Environment': 'production'
                }
            )
            
            print(f"EKS cluster {cluster_name} creation initiated")
            return response['cluster']['arn']
            
        except Exception as e:
            print(f"Error creating EKS cluster: {str(e)}")
            return None
    
    def create_nodegroup(self, cluster_name: str, nodegroup_name: str, 
                        instance_types: List[str], capacity_type: str = 'ON_DEMAND'):
        """Create EKS node group."""
        try:
            response = self.eks_client.create_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                nodeRole=self._get_node_role_arn(),
                subnets=self._get_subnet_ids(),
                instanceTypes=instance_types,
                capacityType=capacity_type,
                scalingConfig={
                    'minSize': 2,
                    'maxSize': 10,
                    'desiredSize': 3
                },
                updateConfig={
                    'maxUnavailable': 1
                },
                tags={
                    'Project': 'aws-container-platform',
                    'NodeGroup': nodegroup_name
                }
            )
            
            print(f"Node group {nodegroup_name} creation initiated")
            return response['nodegroup']['nodegroupArn']
            
        except Exception as e:
            print(f"Error creating node group: {str(e)}")
            return None
    
    def install_addon(self, cluster_name: str, addon_name: str, addon_version: str):
        """Install EKS addon."""
        try:
            response = self.eks_client.create_addon(
                clusterName=cluster_name,
                addonName=addon_name,
                addonVersion=addon_version,
                resolveConflicts='OVERWRITE'
            )
            
            print(f"Addon {addon_name} installation initiated")
            return response['addon']['addonArn']
            
        except Exception as e:
            print(f"Error installing addon: {str(e)}")
            return None
    
    def update_kubeconfig(self, cluster_name: str, region: str):
        """Update kubeconfig for cluster access."""
        try:
            subprocess.run([
                'aws', 'eks', 'update-kubeconfig',
                '--name', cluster_name,
                '--region', region
            ], check=True)
            
            print(f"Kubeconfig updated for cluster {cluster_name}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error updating kubeconfig: {str(e)}")
    
    def get_cluster_status(self, cluster_name: str) -> Dict[str, Any]:
        """Get cluster status and information."""
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = response['cluster']
            
            return {
                'name': cluster['name'],
                'arn': cluster['arn'],
                'version': cluster['version'],
                'status': cluster['status'],
                'endpoint': cluster['endpoint'],
                'platform_version': cluster['platformVersion'],
                'created_at': cluster['createdAt'].isoformat()
            }
            
        except Exception as e:
            print(f"Error getting cluster status: {str(e)}")
            return {}
    
    def _get_cluster_role_arn(self) -> str:
        """Get EKS cluster role ARN."""
        try:
            response = self.iam_client.get_role(RoleName='eks-cluster-role')
            return response['Role']['Arn']
        except Exception as e:
            print(f"Error getting cluster role: {str(e)}")
            return None
    
    def _get_node_role_arn(self) -> str:
        """Get EKS node role ARN."""
        try:
            response = self.iam_client.get_role(RoleName='eks-node-role')
            return response['Role']['Arn']
        except Exception as e:
            print(f"Error getting node role: {str(e)}")
            return None
    
    def _get_subnet_ids(self) -> List[str]:
        """Get subnet IDs for EKS cluster."""
        try:
            response = self.ec2_client.describe_subnets(
                Filters=[
                    {
                        'Name': 'tag:kubernetes.io/role/elb',
                        'Values': ['1']
                    }
                ]
            )
            return [subnet['SubnetId'] for subnet in response['Subnets']]
        except Exception as e:
            print(f"Error getting subnet IDs: {str(e)}")
            return []
    
    def _get_security_group_ids(self) -> List[str]:
        """Get security group IDs for EKS cluster."""
        try:
            response = self.ec2_client.describe_security_groups(
                Filters=[
                    {
                        'Name': 'group-name',
                        'Values': ['eks-cluster-sg']
                    }
                ]
            )
            return [sg['GroupId'] for sg in response['SecurityGroups']]
        except Exception as e:
            print(f"Error getting security group IDs: {str(e)}")
            return []
```

#### Kubernetes Manager
```python
# python/container_orchestration/kubernetes_manager.py
import yaml
import subprocess
import logging
from typing import List, Dict, Any
from kubernetes import client, config

class KubernetesManager:
    """
    Kubernetes resource manager for container orchestration.
    """
    
    def __init__(self):
        try:
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
        except Exception as e:
            print(f"Error initializing Kubernetes client: {str(e)}")
    
    def create_namespace(self, namespace: str):
        """Create Kubernetes namespace."""
        try:
            namespace_obj = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            self.v1.create_namespace(namespace_obj)
            print(f"Namespace {namespace} created successfully")
        except Exception as e:
            print(f"Error creating namespace: {str(e)}")
    
    def deploy_application(self, namespace: str, deployment_config: Dict[str, Any]):
        """Deploy application to Kubernetes."""
        try:
            # Create deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=deployment_config['name'],
                    namespace=namespace
                ),
                spec=client.V1DeploymentSpec(
                    replicas=deployment_config.get('replicas', 3),
                    selector=client.V1LabelSelector(
                        match_labels=deployment_config['labels']
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels=deployment_config['labels']
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=container['name'],
                                    image=container['image'],
                                    ports=[
                                        client.V1ContainerPort(
                                            container_port=port['port']
                                        ) for port in container.get('ports', [])
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        requests=container.get('requests', {}),
                                        limits=container.get('limits', {})
                                    )
                                ) for container in deployment_config['containers']
                            ]
                        )
                    )
                )
            )
            
            self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            print(f"Deployment {deployment_config['name']} created successfully")
            
        except Exception as e:
            print(f"Error deploying application: {str(e)}")
    
    def create_service(self, namespace: str, service_config: Dict[str, Any]):
        """Create Kubernetes service."""
        try:
            service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=service_config['name'],
                    namespace=namespace
                ),
                spec=client.V1ServiceSpec(
                    selector=service_config['selector'],
                    ports=[
                        client.V1ServicePort(
                            port=port['port'],
                            target_port=port['target_port'],
                            protocol=port.get('protocol', 'TCP')
                        ) for port in service_config['ports']
                    ],
                    type=service_config.get('type', 'ClusterIP')
                )
            )
            
            self.v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            
            print(f"Service {service_config['name']} created successfully")
            
        except Exception as e:
            print(f"Error creating service: {str(e)}")
    
    def create_ingress(self, namespace: str, ingress_config: Dict[str, Any]):
        """Create Kubernetes ingress."""
        try:
            ingress = client.V1Ingress(
                metadata=client.V1ObjectMeta(
                    name=ingress_config['name'],
                    namespace=namespace,
                    annotations=ingress_config.get('annotations', {})
                ),
                spec=client.V1IngressSpec(
                    rules=[
                        client.V1IngressRule(
                            host=rule['host'],
                            http=client.V1HTTPIngressRuleValue(
                                paths=[
                                    client.V1HTTPIngressPath(
                                        path=path['path'],
                                        path_type=path.get('path_type', 'Prefix'),
                                        backend=client.V1IngressBackend(
                                            service=client.V1IngressServiceBackend(
                                                name=path['service']['name'],
                                                port=client.V1ServiceBackendPort(
                                                    number=path['service']['port']
                                                )
                                            )
                                        )
                                    ) for path in rule['paths']
                                ]
                            )
                        ) for rule in ingress_config['rules']
                    ]
                )
            )
            
            self.networking_v1.create_namespaced_ingress(
                namespace=namespace,
                body=ingress
            )
            
            print(f"Ingress {ingress_config['name']} created successfully")
            
        except Exception as e:
            print(f"Error creating ingress: {str(e)}")
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int):
        """Scale deployment to specified number of replicas."""
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={'spec': {'replicas': replicas}}
            )
            
            print(f"Deployment {deployment_name} scaled to {replicas} replicas")
            
        except Exception as e:
            print(f"Error scaling deployment: {str(e)}")
    
    def get_pod_status(self, namespace: str) -> List[Dict[str, Any]]:
        """Get pod status in namespace."""
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            
            pod_status = []
            for pod in pods.items:
                pod_status.append({
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'ready': pod.status.ready,
                    'restarts': pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0
                })
            
            return pod_status
            
        except Exception as e:
            print(f"Error getting pod status: {str(e)}")
            return []
```

### Terraform Implementation

#### EKS Cluster Module
```hcl
# terraform/modules/eks_cluster/main.tf
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    security_group_ids      = var.security_group_ids
    endpoint_public_access  = true
    endpoint_private_access = true
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]

  tags = {
    Name        = var.cluster_name
    Environment = var.environment
    Project     = var.project_name
  }
}

# EKS Cluster IAM Role
resource "aws_iam_role" "eks_cluster" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.cluster_name}-cluster-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}

# Node Groups
resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = each.key
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = var.subnet_ids

  instance_types = each.value.instance_types
  capacity_type  = each.value.capacity_type

  scaling_config {
    desired_size = each.value.desired_size
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }

  update_config {
    max_unavailable = each.value.max_unavailable
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ec2_container_registry_read_only,
  ]

  tags = {
    Name        = "${var.cluster_name}-${each.key}"
    Environment = var.environment
    NodeGroup   = each.key
  }
}

# Node Group IAM Role
resource "aws_iam_role" "eks_node_group" {
  name = "${var.cluster_name}-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.cluster_name}-node-group-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_read_only" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group.name
}

# EKS Addons
resource "aws_eks_addon" "vpc_cni" {
  cluster_name = aws_eks_cluster.main.name
  addon_name   = "vpc-cni"
  addon_version = "v1.14.1-eksbuild.1"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = {
    Name        = "${var.cluster_name}-vpc-cni"
    Environment = var.environment
  }
}

resource "aws_eks_addon" "coredns" {
  cluster_name = aws_eks_cluster.main.name
  addon_name   = "coredns"
  addon_version = "v1.10.1-eksbuild.1"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_addon.vpc_cni]

  tags = {
    Name        = "${var.cluster_name}-coredns"
    Environment = var.environment
  }
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = aws_eks_cluster.main.name
  addon_name   = "kube-proxy"
  addon_version = "v1.27.4-eksbuild.1"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_addon.vpc_cni]

  tags = {
    Name        = "${var.cluster_name}-kube-proxy"
    Environment = var.environment
  }
}
```

## 📊 Monitoring Dashboard

### Kubernetes Dashboard
```json
{
  "dashboard": {
    "title": "Kubernetes Cluster Overview",
    "panels": [
      {
        "title": "Cluster CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(container_cpu_usage_seconds_total{container!=\"\"}[5m])) by (pod)",
            "legendFormat": "{{pod}}"
          }
        ]
      },
      {
        "title": "Cluster Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(container_memory_usage_bytes{container!=\"\"}) by (pod)",
            "legendFormat": "{{pod}}"
          }
        ]
      },
      {
        "title": "Pod Status",
        "type": "stat",
        "targets": [
          {
            "expr": "count(kube_pod_status_phase)",
            "legendFormat": "Total Pods"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Security Features

### Container Security
- **Image Scanning** - Automated vulnerability scanning
- **Image Signing** - Digital signature verification
- **Runtime Security** - Container runtime protection
- **Network Policies** - Pod-to-pod communication control
- **RBAC** - Role-based access control

### Compliance
- **CIS Benchmarks** - Kubernetes security benchmarks
- **Pod Security Policies** - Security context enforcement
- **Network Policies** - Network segmentation
- **Audit Logging** - Comprehensive audit trails

## 📈 Performance Optimization

### Auto-scaling
```python
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Resource Management
- **Resource Quotas** - Namespace resource limits
- **Limit Ranges** - Pod resource constraints
- **Priority Classes** - Pod scheduling priorities
- **Node Affinity** - Pod placement strategies

## 🔄 CI/CD Integration

### GitHub Actions Workflow
```yaml
# cicd/github-actions/deploy.yml
name: Deploy to EKS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --name production-cluster --region us-east-1
    
    - name: Deploy to EKS
      run: |
        kubectl apply -f kubernetes/
        kubectl rollout status deployment/app-deployment
```

## 📞 Support and Resources

### Documentation
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Istio Documentation](https://istio.io/docs/)

### Community Resources
- [AWS Container Blog](https://aws.amazon.com/blogs/containers/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Charts Repository](https://github.com/helm/charts)

### Professional Services
- AWS Professional Services
- AWS Container Competency Partners
- AWS Managed Kubernetes Services

## 📄 License

This project is provided as-is for educational and demonstration purposes. Please review and modify according to your specific containerization requirements and security policies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 Changelog

### Version 1.0.0
- Initial release with comprehensive container platform
- EKS cluster management and automation
- Kubernetes resource orchestration
- Service mesh integration (Istio)
- CI/CD pipeline automation
- Monitoring and observability setup
- Security and compliance features
- Multi-environment support
- Terraform and CloudFormation implementations
- Python automation scripts and Kubernetes operators
