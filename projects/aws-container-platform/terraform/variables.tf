# AWS Container & Kubernetes Platform - Variables
# This file defines all the input variables for the Terraform configuration

# General Configuration
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-container-platform"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "production"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = false
}

# EKS Cluster Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "aws-container-platform"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "cluster_endpoint_public_access" {
  description = "Whether the Amazon EKS public API server endpoint is enabled"
  type        = bool
  default     = true
}

variable "cluster_endpoint_private_access" {
  description = "Whether the Amazon EKS private API server endpoint is enabled"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks which can access the Amazon EKS public API server endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cluster_encryption_enabled" {
  description = "Whether to enable EKS cluster encryption"
  type        = bool
  default     = true
}

variable "cluster_log_types" {
  description = "A list of the desired control plane logging to enable"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

# Node Group Configuration
variable "node_instance_types" {
  description = "List of instance types for the node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "Type of capacity associated with the EKS Node Group"
  type        = string
  default     = "ON_DEMAND"
  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "Node capacity type must be ON_DEMAND or SPOT."
  }
}

variable "node_min_size" {
  description = "Minimum number of nodes in the node group"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of nodes in the node group"
  type        = number
  default     = 10
}

variable "node_desired_size" {
  description = "Desired number of nodes in the node group"
  type        = number
  default     = 3
}

variable "node_disk_size" {
  description = "Disk size in GiB for worker nodes"
  type        = number
  default     = 50
}

variable "node_ami_type" {
  description = "Type of Amazon Machine Image (AMI) associated with the EKS Node Group"
  type        = string
  default     = "AL2_x86_64"
  validation {
    condition = contains([
      "AL2_x86_64", "AL2_x86_64_GPU", "AL2_ARM_64", "CUSTOM", "BOTTLEROCKET_ARM_64", "BOTTLEROCKET_x86_64"
    ], var.node_ami_type)
    error_message = "Node AMI type must be a valid EKS AMI type."
  }
}

variable "node_remote_access_enabled" {
  description = "Whether to enable remote access to nodes"
  type        = bool
  default     = false
}

variable "node_ssh_key_name" {
  description = "EC2 Key Pair name for SSH access to nodes"
  type        = string
  default     = ""
}

variable "node_ssh_cidr_blocks" {
  description = "List of CIDR blocks for SSH access to nodes"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_taints" {
  description = "List of Kubernetes taints to apply to the node group"
  type = list(object({
    key    = string
    value  = string
    effect = string
  }))
  default = []
}

# ECR Configuration
variable "ecr_repositories" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default     = ["app", "nginx", "redis"]
}

# Kubernetes Configuration
variable "kubernetes_namespaces" {
  description = "List of Kubernetes namespaces to create"
  type        = list(string)
  default     = ["default", "kube-system", "monitoring", "logging"]
}

variable "kubernetes_config_maps" {
  description = "Map of Kubernetes ConfigMaps to create"
  type = map(object({
    name      = string
    namespace = string
    labels    = map(string)
    data      = map(string)
  }))
  default = {}
}

variable "kubernetes_secrets" {
  description = "Map of Kubernetes Secrets to create"
  type = map(object({
    name      = string
    namespace = string
    labels    = map(string)
    data      = map(string)
    type      = string
  }))
  default = {}
}

# Helm Charts Configuration
variable "helm_charts" {
  description = "Map of Helm charts to install"
  type = map(object({
    name             = string
    repository       = string
    chart            = string
    version          = string
    namespace        = string
    create_namespace = bool
    wait             = bool
    timeout          = number
    values           = list(string)
  }))
  default = {
    nginx_ingress = {
      name             = "nginx-ingress"
      repository       = "https://kubernetes.github.io/ingress-nginx"
      chart            = "ingress-nginx"
      version          = "4.7.1"
      namespace        = "ingress-nginx"
      create_namespace = true
      wait             = true
      timeout          = 300
      values           = []
    }
    metrics_server = {
      name             = "metrics-server"
      repository       = "https://kubernetes-sigs.github.io/metrics-server/"
      chart            = "metrics-server"
      version          = "3.10.0"
      namespace        = "kube-system"
      create_namespace = false
      wait             = true
      timeout          = 300
      values           = []
    }
  }
}

# Monitoring Configuration
variable "create_alarms" {
  description = "Whether to create CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alarm_sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  type        = string
  default     = null
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Backup Configuration
variable "create_backup_bucket" {
  description = "Whether to create S3 bucket for cluster backups"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}