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
  default     = "aws-serverless-platform"
}

variable "vpc_id" {
  description = "VPC ID for Lambda functions"
  type        = string
  default     = ""
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs for Lambda functions"
  type        = list(string)
  default     = []
}

# DynamoDB variables
variable "create_dynamodb_tables" {
  description = "Whether to create DynamoDB tables"
  type        = bool
  default     = true
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string
  default     = "PAY_PER_REQUEST"
  validation {
    condition     = contains(["PROVISIONED", "PAY_PER_REQUEST"], var.dynamodb_billing_mode)
    error_message = "DynamoDB billing mode must be either PROVISIONED or PAY_PER_REQUEST."
  }
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units"
  type        = number
  default     = 5
}

# SQS variables
variable "create_sqs_queues" {
  description = "Whether to create SQS queues"
  type        = bool
  default     = true
}

variable "sqs_visibility_timeout" {
  description = "SQS visibility timeout in seconds"
  type        = number
  default     = 300
}

variable "sqs_message_retention" {
  description = "SQS message retention period in seconds"
  type        = number
  default     = 1209600
}

variable "sqs_max_receive_count" {
  description = "Maximum number of times a message can be received before going to DLQ"
  type        = number
  default     = 3
}

# SNS variables
variable "create_sns_topics" {
  description = "Whether to create SNS topics"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for notifications"
  type        = string
  default     = ""
}

variable "alert_email" {
  description = "Email address for system alerts"
  type        = string
  default     = ""
}

# Lambda variables
variable "create_lambda_functions" {
  description = "Whether to create Lambda functions"
  type        = bool
  default     = true
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 256
}

variable "lambda_environment_variables" {
  description = "Environment variables for Lambda functions"
  type        = map(string)
  default     = {}
}

# Step Functions variables
variable "create_step_functions" {
  description = "Whether to create Step Functions state machines"
  type        = bool
  default     = true
}

variable "stepfunctions_log_level" {
  description = "Step Functions log level"
  type        = string
  default     = "ERROR"
  validation {
    condition     = contains(["ALL", "ERROR", "FATAL", "OFF"], var.stepfunctions_log_level)
    error_message = "Step Functions log level must be one of: ALL, ERROR, FATAL, OFF."
  }
}

# API Gateway variables
variable "create_api_gateway" {
  description = "Whether to create API Gateway"
  type        = bool
  default     = true
}

variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "prod"
}

variable "api_gateway_throttle_rate" {
  description = "API Gateway throttle rate"
  type        = number
  default     = 1000
}

variable "api_gateway_throttle_burst" {
  description = "API Gateway throttle burst"
  type        = number
  default     = 2000
}

# CloudWatch variables
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "create_cloudwatch_alarms" {
  description = "Whether to create CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alarm_threshold_lambda_errors" {
  description = "Threshold for Lambda errors alarm"
  type        = number
  default     = 5
}

variable "alarm_threshold_dynamodb_throttles" {
  description = "Threshold for DynamoDB throttles alarm"
  type        = number
  default     = 10
}

# EventBridge variables
variable "create_eventbridge_rules" {
  description = "Whether to create EventBridge rules"
  type        = bool
  default     = true
}

variable "eventbridge_schedule_expression" {
  description = "EventBridge schedule expression"
  type        = string
  default     = "rate(5 minutes)"
}

# X-Ray variables
variable "enable_xray_tracing" {
  description = "Whether to enable X-Ray tracing"
  type        = bool
  default     = true
}

variable "xray_sampling_rate" {
  description = "X-Ray sampling rate (0.0 to 1.0)"
  type        = number
  default     = 0.1
  validation {
    condition     = var.xray_sampling_rate >= 0.0 && var.xray_sampling_rate <= 1.0
    error_message = "X-Ray sampling rate must be between 0.0 and 1.0."
  }
}

# Security variables
variable "enable_encryption" {
  description = "Whether to enable encryption for all resources"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}

variable "enable_point_in_time_recovery" {
  description = "Whether to enable point-in-time recovery for DynamoDB"
  type        = bool
  default     = true
}

# Monitoring variables
variable "enable_detailed_monitoring" {
  description = "Whether to enable detailed monitoring"
  type        = bool
  default     = true
}

variable "monitoring_retention_days" {
  description = "Monitoring data retention in days"
  type        = number
  default     = 30
}

# Cost optimization variables
variable "enable_cost_optimization" {
  description = "Whether to enable cost optimization features"
  type        = bool
  default     = true
}

variable "lambda_provisioned_concurrency" {
  description = "Lambda provisioned concurrency"
  type        = number
  default     = 0
}

variable "dynamodb_auto_scaling_enabled" {
  description = "Whether to enable DynamoDB auto scaling"
  type        = bool
  default     = false
}

# Backup variables
variable "enable_backups" {
  description = "Whether to enable backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 30
}

# Compliance variables
variable "compliance_requirements" {
  description = "Compliance requirements (e.g., HIPAA, SOC2, PCI)"
  type        = list(string)
  default     = []
}

variable "data_classification" {
  description = "Data classification level"
  type        = string
  default     = "internal"
  validation {
    condition     = contains(["public", "internal", "confidential", "restricted"], var.data_classification)
    error_message = "Data classification must be one of: public, internal, confidential, restricted."
  }
}

# Performance variables
variable "performance_requirements" {
  description = "Performance requirements"
  type        = map(string)
  default = {
    response_time = "500ms"
    throughput    = "1000rps"
    availability  = "99.9%"
  }
}

# Disaster recovery variables
variable "enable_disaster_recovery" {
  description = "Whether to enable disaster recovery"
  type        = bool
  default     = false
}

variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "us-west-2"
}

# Development variables
variable "enable_development_features" {
  description = "Whether to enable development features"
  type        = bool
  default     = false
}

variable "debug_mode" {
  description = "Whether to enable debug mode"
  type        = bool
  default     = false
}

variable "enable_hot_reload" {
  description = "Whether to enable hot reload for development"
  type        = bool
  default     = false
}

# Testing variables
variable "enable_testing" {
  description = "Whether to enable testing features"
  type        = bool
  default     = false
}

variable "test_data_generation" {
  description = "Whether to generate test data"
  type        = bool
  default     = false
}

variable "load_testing_enabled" {
  description = "Whether to enable load testing"
  type        = bool
  default     = false
}

# Custom tags
variable "custom_tags" {
  description = "Custom tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Resource limits
variable "max_lambda_functions" {
  description = "Maximum number of Lambda functions"
  type        = number
  default     = 10
}

variable "max_dynamodb_tables" {
  description = "Maximum number of DynamoDB tables"
  type        = number
  default     = 5
}

variable "max_sqs_queues" {
  description = "Maximum number of SQS queues"
  type        = number
  default     = 5
}

variable "max_sns_topics" {
  description = "Maximum number of SNS topics"
  type        = number
  default     = 5
}

# Feature flags
variable "feature_flags" {
  description = "Feature flags for enabling/disabling specific features"
  type        = map(bool)
  default = {
    enable_api_versioning     = false
    enable_canary_deployments = false
    enable_blue_green_deploy  = false
    enable_auto_scaling       = false
    enable_circuit_breaker    = false
    enable_retry_mechanisms   = true
    enable_dead_letter_queues = true
    enable_monitoring         = true
    enable_alerting           = true
    enable_logging            = true
  }
}