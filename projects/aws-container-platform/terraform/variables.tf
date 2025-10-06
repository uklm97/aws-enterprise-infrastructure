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

# Node Group Configuration
variable "node_instance_types" {
  description = "Instance types for the EKS managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "Type of capacity associated with the EKS Node Group"
  type        = string
  default     = "ON_DEMAND"
  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "Node capacity type must be either ON_DEMAND or SPOT."
  }
}

variable "node_min_size" {
  description = "Minimum number of nodes in the EKS managed node group"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of nodes in the EKS managed node group"
  type        = number
  default     = 10
}

variable "node_desired_size" {
  description = "Desired number of nodes in the EKS managed node group"
  type        = number
  default     = 3
}

variable "node_disk_size" {
  description = "Disk size in GiB for worker nodes"
  type        = number
  default     = 50
}

variable "node_disk_type" {
  description = "Disk type for worker nodes"
  type        = string
  default     = "gp3"
}

# Spot Instance Configuration
variable "spot_instance_types" {
  description = "Instance types for the spot node group"
  type        = list(string)
  default     = ["t3.medium", "t3.large", "t3.xlarge"]
}

variable "spot_min_size" {
  description = "Minimum number of nodes in the spot node group"
  type        = number
  default     = 0
}

variable "spot_max_size" {
  description = "Maximum number of nodes in the spot node group"
  type        = number
  default     = 5
}

variable "spot_desired_size" {
  description = "Desired number of nodes in the spot node group"
  type        = number
  default     = 0
}

# ECR Configuration
variable "ecr_repositories" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default     = ["app", "api", "frontend", "worker"]
}

# Kubernetes Configuration
variable "kubernetes_namespaces" {
  description = "List of Kubernetes namespaces to create"
  type        = list(string)
  default     = ["default", "kube-system", "kube-public", "kube-node-lease", "monitoring", "logging", "ingress-nginx"]
}

# Helm Chart Configuration
variable "install_aws_load_balancer_controller" {
  description = "Whether to install AWS Load Balancer Controller"
  type        = bool
  default     = true
}

variable "aws_load_balancer_controller_version" {
  description = "Version of AWS Load Balancer Controller"
  type        = string
  default     = "1.6.2"
}

variable "install_cluster_autoscaler" {
  description = "Whether to install Cluster Autoscaler"
  type        = bool
  default     = true
}

variable "cluster_autoscaler_version" {
  description = "Version of Cluster Autoscaler"
  type        = string
  default     = "9.29.0"
}

variable "install_metrics_server" {
  description = "Whether to install Metrics Server"
  type        = bool
  default     = true
}

variable "metrics_server_version" {
  description = "Version of Metrics Server"
  type        = string
  default     = "3.10.0"
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Monitoring Configuration
variable "create_alarms" {
  description = "Whether to create CloudWatch alarms"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}