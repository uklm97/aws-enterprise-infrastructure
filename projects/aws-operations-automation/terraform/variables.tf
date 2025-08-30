variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-operations-automation"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
  
  validation {
    condition     = var.log_retention_days >= 1 && var.log_retention_days <= 3653
    error_message = "Log retention days must be between 1 and 3653."
  }
}

variable "enable_email_notifications" {
  description = "Enable email notifications via SNS"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for notifications"
  type        = string
  default     = "admin@company.com"
}

variable "instance_scheduling" {
  description = "Instance scheduling configuration"
  type = object({
    enabled = bool
    start_time = string
    stop_time = string
    timezone = string
    weekend_shutdown = bool
    holiday_shutdown = bool
  })
  default = {
    enabled = true
    start_time = "08:00"
    stop_time = "18:00"
    timezone = "UTC"
    weekend_shutdown = true
    holiday_shutdown = true
  }
}

variable "backup_scheduling" {
  description = "Backup scheduling configuration"
  type = object({
    daily_enabled = bool
    daily_time = string
    daily_retention_days = number
    
    weekly_enabled = bool
    weekly_day = string
    weekly_time = string
    weekly_retention_days = number
    
    monthly_enabled = bool
    monthly_day = string
    monthly_time = string
    monthly_retention_days = number
  })
  default = {
    daily_enabled = true
    daily_time = "02:00"
    daily_retention_days = 7
    
    weekly_enabled = true
    weekly_day = "sunday"
    weekly_time = "03:00"
    weekly_retention_days = 30
    
    monthly_enabled = true
    monthly_day = "1st"
    monthly_time = "04:00"
    monthly_retention_days = 90
  }
}

variable "cross_region_backup" {
  description = "Cross-region backup configuration"
  type = object({
    enabled = bool
    destination_regions = list(string)
    retention_days = number
  })
  default = {
    enabled = true
    destination_regions = ["us-west-2", "eu-west-1"]
    retention_days = 365
  }
}

variable "lambda_config" {
  description = "Lambda function configuration"
  type = object({
    timeout = number
    memory_size = number
    runtime = string
  })
  default = {
    timeout = 300
    memory_size = 256
    runtime = "python3.9"
  }
}

variable "monitoring" {
  description = "Monitoring configuration"
  type = object({
    enable_dashboard = bool
    enable_alarms = bool
    alarm_threshold = number
  })
  default = {
    enable_dashboard = true
    enable_alarms = true
    alarm_threshold = 0
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Owner       = "DevOps"
    Purpose     = "Automation"
    CostCenter  = "IT"
  }
}
