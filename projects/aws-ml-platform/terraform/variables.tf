variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "aws-ml-platform"
}

# VPC Configuration
variable "vpc_id" {
  description = "VPC ID for SageMaker domain"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for SageMaker domain"
  type        = list(string)
  default     = []
}

# S3 Configuration
variable "create_s3_bucket" {
  description = "Whether to create S3 bucket for ML data"
  type        = bool
  default     = true
}

# IAM Configuration
variable "create_iam_roles" {
  description = "Whether to create IAM roles"
  type        = bool
  default     = true
}

# SageMaker Configuration
variable "create_sagemaker_domain" {
  description = "Whether to create SageMaker domain"
  type        = bool
  default     = true
}

variable "create_notebook_instance" {
  description = "Whether to create SageMaker notebook instance"
  type        = bool
  default     = true
}

variable "notebook_instance_type" {
  description = "SageMaker notebook instance type"
  type        = string
  default     = "ml.t3.medium"
}

variable "create_model_package_group" {
  description = "Whether to create model package group"
  type        = bool
  default     = true
}

variable "create_experiment" {
  description = "Whether to create SageMaker experiment"
  type        = bool
  default     = true
}

variable "create_pipeline" {
  description = "Whether to create SageMaker pipeline"
  type        = bool
  default     = true
}

variable "pipeline_definition" {
  description = "SageMaker pipeline definition"
  type        = string
  default     = ""
}

# Endpoint Configuration
variable "create_endpoint_configuration" {
  description = "Whether to create endpoint configuration"
  type        = bool
  default     = true
}

variable "create_endpoint" {
  description = "Whether to create SageMaker endpoint"
  type        = bool
  default     = true
}

variable "model_name" {
  description = "SageMaker model name for endpoint"
  type        = string
  default     = ""
}

variable "initial_instance_count" {
  description = "Initial instance count for endpoint"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "Instance type for endpoint"
  type        = string
  default     = "ml.m5.large"
}

# Monitoring Configuration
variable "create_monitoring_schedule" {
  description = "Whether to create monitoring schedule"
  type        = bool
  default     = true
}

variable "monitoring_schedule_expression" {
  description = "Monitoring schedule expression"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM
}

variable "create_data_quality_job" {
  description = "Whether to create data quality job definition"
  type        = bool
  default     = true
}

variable "data_quality_image_uri" {
  description = "Data quality monitoring image URI"
  type        = string
  default     = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-model-monitor:latest"
}

variable "create_model_quality_job" {
  description = "Whether to create model quality job definition"
  type        = bool
  default     = true
}

variable "model_quality_image_uri" {
  description = "Model quality monitoring image URI"
  type        = string
  default     = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-model-monitor:latest"
}

variable "create_bias_job" {
  description = "Whether to create bias job definition"
  type        = bool
  default     = true
}

variable "bias_image_uri" {
  description = "Bias monitoring image URI"
  type        = string
  default     = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-model-monitor:latest"
}

variable "create_explainability_job" {
  description = "Whether to create explainability job definition"
  type        = bool
  default     = true
}

variable "explainability_image_uri" {
  description = "Explainability monitoring image URI"
  type        = string
  default     = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-model-monitor:latest"
}

# ECR Configuration
variable "create_ecr_repository" {
  description = "Whether to create ECR repository"
  type        = bool
  default     = true
}

# Lambda Configuration
variable "create_lambda_functions" {
  description = "Whether to create Lambda functions"
  type        = bool
  default     = true
}

# EventBridge Configuration
variable "create_eventbridge_rules" {
  description = "Whether to create EventBridge rules"
  type        = bool
  default     = true
}

variable "automation_schedule_expression" {
  description = "Automation schedule expression"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM
}

# CloudWatch Configuration
variable "create_dashboard" {
  description = "Whether to create CloudWatch dashboard"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

# SNS Configuration
variable "create_sns_topic" {
  description = "Whether to create SNS topic"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for notifications"
  type        = string
  default     = ""
}

# API Gateway Configuration
variable "create_api_gateway" {
  description = "Whether to create API Gateway"
  type        = bool
  default     = true
}

# ML Platform Features
variable "enable_mlops" {
  description = "Enable MLOps features"
  type        = bool
  default     = true
}

variable "enable_experiment_tracking" {
  description = "Enable experiment tracking"
  type        = bool
  default     = true
}

variable "enable_model_monitoring" {
  description = "Enable model monitoring"
  type        = bool
  default     = true
}

variable "enable_hyperparameter_tuning" {
  description = "Enable hyperparameter tuning"
  type        = bool
  default     = true
}

variable "enable_automated_ml" {
  description = "Enable automated ML"
  type        = bool
  default     = true
}

variable "enable_batch_inference" {
  description = "Enable batch inference"
  type        = bool
  default     = true
}

variable "enable_real_time_inference" {
  description = "Enable real-time inference"
  type        = bool
  default     = true
}

# Model Configuration
variable "model_framework" {
  description = "ML framework (tensorflow, pytorch, sklearn, xgboost)"
  type        = string
  default     = "tensorflow"
  validation {
    condition     = contains(["tensorflow", "pytorch", "sklearn", "xgboost", "huggingface"], var.model_framework)
    error_message = "Model framework must be one of: tensorflow, pytorch, sklearn, xgboost, huggingface."
  }
}

variable "model_version" {
  description = "Model framework version"
  type        = string
  default     = "2.13.0"
}

variable "python_version" {
  description = "Python version"
  type        = string
  default     = "3.9"
}

# Training Configuration
variable "training_instance_type" {
  description = "Training instance type"
  type        = string
  default     = "ml.m5.large"
}

variable "training_instance_count" {
  description = "Training instance count"
  type        = number
  default     = 1
}

variable "training_volume_size" {
  description = "Training volume size in GB"
  type        = number
  default     = 30
}

# Inference Configuration
variable "inference_instance_type" {
  description = "Inference instance type"
  type        = string
  default     = "ml.m5.large"
}

variable "inference_instance_count" {
  description = "Inference instance count"
  type        = number
  default     = 1
}

variable "inference_volume_size" {
  description = "Inference volume size in GB"
  type        = number
  default     = 30
}

# Data Configuration
variable "data_format" {
  description = "Data format (csv, json, parquet, tfrecord)"
  type        = string
  default     = "csv"
  validation {
    condition     = contains(["csv", "json", "parquet", "tfrecord", "recordio"], var.data_format)
    error_message = "Data format must be one of: csv, json, parquet, tfrecord, recordio."
  }
}

variable "data_compression" {
  description = "Data compression type"
  type        = string
  default     = "gzip"
  validation {
    condition     = contains(["gzip", "bzip2", "xz", "none"], var.data_compression)
    error_message = "Data compression must be one of: gzip, bzip2, xz, none."
  }
}

# Security Configuration
variable "enable_encryption" {
  description = "Enable encryption for all resources"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
  default     = ""
}

variable "enable_network_isolation" {
  description = "Enable network isolation for SageMaker"
  type        = bool
  default     = false
}

variable "enable_inter_container_traffic_encryption" {
  description = "Enable inter-container traffic encryption"
  type        = bool
  default     = false
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = true
}

variable "monitoring_retention_days" {
  description = "Monitoring data retention in days"
  type        = number
  default     = 30
}

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logs"
  type        = bool
  default     = true
}

variable "log_level" {
  description = "Log level (DEBUG, INFO, WARN, ERROR)"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARN", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARN, ERROR."
  }
}

# Cost Optimization
variable "enable_spot_training" {
  description = "Enable spot training for cost optimization"
  type        = bool
  default     = true
}

variable "enable_managed_spot_training" {
  description = "Enable managed spot training"
  type        = bool
  default     = true
}

variable "max_wait_time" {
  description = "Maximum wait time for spot training in seconds"
  type        = number
  default     = 3600
}

variable "checkpoint_config" {
  description = "Checkpoint configuration for training"
  type        = map(string)
  default     = {}
}

# Custom Tags
variable "custom_tags" {
  description = "Custom tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Feature Flags
variable "feature_flags" {
  description = "Feature flags for ML platform"
  type        = map(bool)
  default = {
    enable_mlops                    = true
    enable_experiment_tracking      = true
    enable_model_monitoring         = true
    enable_hyperparameter_tuning    = true
    enable_automated_ml             = true
    enable_batch_inference          = true
    enable_real_time_inference      = true
    enable_data_quality_monitoring  = true
    enable_model_quality_monitoring = true
    enable_bias_monitoring          = true
    enable_explainability_monitoring = true
    enable_automated_retraining     = true
    enable_model_versioning         = true
    enable_ab_testing               = true
    enable_cost_optimization        = true
  }
}

# ML Pipeline Configuration
variable "pipeline_stages" {
  description = "ML pipeline stages"
  type        = list(string)
  default     = ["data_ingestion", "data_preprocessing", "feature_engineering", "model_training", "model_evaluation", "model_deployment"]
}

variable "pipeline_parallelism" {
  description = "Pipeline parallelism level"
  type        = number
  default     = 1
}

variable "pipeline_timeout" {
  description = "Pipeline timeout in seconds"
  type        = number
  default     = 3600
}

# Experiment Configuration
variable "experiment_tracking_backend" {
  description = "Experiment tracking backend (sagemaker, mlflow, wandb)"
  type        = string
  default     = "sagemaker"
  validation {
    condition     = contains(["sagemaker", "mlflow", "wandb"], var.experiment_tracking_backend)
    error_message = "Experiment tracking backend must be one of: sagemaker, mlflow, wandb."
  }
}

variable "experiment_retention_days" {
  description = "Experiment retention in days"
  type        = number
  default     = 90
}

# Model Registry Configuration
variable "model_registry_backend" {
  description = "Model registry backend (sagemaker, mlflow, custom)"
  type        = string
  default     = "sagemaker"
  validation {
    condition     = contains(["sagemaker", "mlflow", "custom"], var.model_registry_backend)
    error_message = "Model registry backend must be one of: sagemaker, mlflow, custom."
  }
}

variable "model_approval_workflow" {
  description = "Model approval workflow configuration"
  type        = map(any)
  default     = {}
}

# Deployment Configuration
variable "deployment_strategy" {
  description = "Deployment strategy (blue_green, canary, rolling)"
  type        = string
  default     = "blue_green"
  validation {
    condition     = contains(["blue_green", "canary", "rolling"], var.deployment_strategy)
    error_message = "Deployment strategy must be one of: blue_green, canary, rolling."
  }
}

variable "auto_scaling_enabled" {
  description = "Enable auto scaling for endpoints"
  type        = bool
  default     = true
}

variable "min_capacity" {
  description = "Minimum capacity for auto scaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum capacity for auto scaling"
  type        = number
  default     = 10
}

variable "target_utilization" {
  description = "Target utilization for auto scaling"
  type        = number
  default     = 70
}