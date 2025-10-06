# AWS Data & Analytics Platform - Variables
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
  default     = "aws-data-analytics"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "production"
}

# Data Lake Configuration
variable "data_lake_bucket_name" {
  description = "Name of the S3 bucket for data lake"
  type        = string
}

# VPC Configuration
variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

# Redshift Configuration
variable "redshift_cluster_identifier" {
  description = "Redshift cluster identifier"
  type        = string
  default     = "data-analytics-cluster"
}

variable "redshift_database_name" {
  description = "Redshift database name"
  type        = string
  default     = "analytics"
}

variable "redshift_master_username" {
  description = "Redshift master username"
  type        = string
  default     = "admin"
}

variable "redshift_master_password" {
  description = "Redshift master password"
  type        = string
  sensitive   = true
}

variable "redshift_node_type" {
  description = "Redshift node type"
  type        = string
  default     = "dc2.large"
  validation {
    condition = contains([
      "dc2.large", "dc2.xlarge", "dc2.2xlarge", "dc2.4xlarge", "dc2.8xlarge",
      "ra3.xlplus", "ra3.4xlarge", "ra3.16xlarge"
    ], var.redshift_node_type)
    error_message = "Redshift node type must be a valid node type."
  }
}

variable "redshift_cluster_type" {
  description = "Redshift cluster type"
  type        = string
  default     = "multi-node"
  validation {
    condition     = contains(["single-node", "multi-node"], var.redshift_cluster_type)
    error_message = "Redshift cluster type must be either single-node or multi-node."
  }
}

variable "redshift_number_of_nodes" {
  description = "Number of Redshift nodes"
  type        = number
  default     = 2
  validation {
    condition     = var.redshift_number_of_nodes >= 1 && var.redshift_number_of_nodes <= 100
    error_message = "Redshift number of nodes must be between 1 and 100."
  }
}

variable "redshift_skip_final_snapshot" {
  description = "Whether to skip final snapshot when destroying cluster"
  type        = bool
  default     = false
}

variable "redshift_snapshot_retention_period" {
  description = "Automated snapshot retention period in days"
  type        = number
  default     = 7
  validation {
    condition     = var.redshift_snapshot_retention_period >= 0 && var.redshift_snapshot_retention_period <= 35
    error_message = "Redshift snapshot retention period must be between 0 and 35 days."
  }
}

variable "redshift_subnet_ids" {
  description = "List of subnet IDs for Redshift cluster"
  type        = list(string)
}

variable "redshift_allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access Redshift"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

# Kinesis Configuration
variable "kinesis_shard_count" {
  description = "Number of Kinesis shards"
  type        = number
  default     = 2
  validation {
    condition     = var.kinesis_shard_count >= 1 && var.kinesis_shard_count <= 500
    error_message = "Kinesis shard count must be between 1 and 500."
  }
}

variable "kinesis_retention_period" {
  description = "Kinesis data retention period in hours"
  type        = number
  default     = 24
  validation {
    condition     = var.kinesis_retention_period >= 24 && var.kinesis_retention_period <= 8760
    error_message = "Kinesis retention period must be between 24 and 8760 hours."
  }
}

# SageMaker Configuration
variable "create_sagemaker_notebook" {
  description = "Whether to create SageMaker notebook instance"
  type        = bool
  default     = true
}

variable "sagemaker_instance_type" {
  description = "SageMaker notebook instance type"
  type        = string
  default     = "ml.t3.medium"
  validation {
    condition = contains([
      "ml.t3.medium", "ml.t3.large", "ml.t3.xlarge", "ml.t3.2xlarge",
      "ml.m5.large", "ml.m5.xlarge", "ml.m5.2xlarge", "ml.m5.4xlarge",
      "ml.p3.2xlarge", "ml.p3.8xlarge", "ml.p3.16xlarge"
    ], var.sagemaker_instance_type)
    error_message = "SageMaker instance type must be a valid instance type."
  }
}

variable "sagemaker_volume_size" {
  description = "SageMaker notebook volume size in GB"
  type        = number
  default     = 20
  validation {
    condition     = var.sagemaker_volume_size >= 5 && var.sagemaker_volume_size <= 16384
    error_message = "SageMaker volume size must be between 5 and 16384 GB."
  }
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
  validation {
    condition     = var.log_retention_days >= 1 && var.log_retention_days <= 3653
    error_message = "Log retention days must be between 1 and 3653."
  }
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