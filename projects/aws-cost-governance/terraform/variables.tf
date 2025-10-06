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
  default     = "aws-cost-governance"
}

# Email configuration
variable "alert_email" {
  description = "Email address for cost alerts"
  type        = string
  default     = ""
}

variable "budget_email" {
  description = "Email address for budget alerts"
  type        = string
  default     = ""
}

variable "report_email" {
  description = "Email address for optimization reports"
  type        = string
  default     = ""
}

# Budget configuration
variable "create_budgets" {
  description = "Whether to create budgets"
  type        = bool
  default     = true
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 1000
}

variable "daily_budget_limit" {
  description = "Daily budget limit in USD"
  type        = number
  default     = 50
}

variable "budget_tags" {
  description = "Tags to filter budget costs"
  type        = list(string)
  default     = ["Environment", "Project", "Component"]
}

# Service-specific budgets
variable "create_service_budgets" {
  description = "Whether to create service-specific budgets"
  type        = bool
  default     = true
}

variable "ec2_budget_limit" {
  description = "EC2 budget limit in USD"
  type        = number
  default     = 500
}

variable "rds_budget_limit" {
  description = "RDS budget limit in USD"
  type        = number
  default     = 200
}

variable "s3_budget_limit" {
  description = "S3 budget limit in USD"
  type        = number
  default     = 100
}

# CloudWatch alarms
variable "create_cloudwatch_alarms" {
  description = "Whether to create CloudWatch cost alarms"
  type        = bool
  default     = true
}

variable "daily_cost_threshold" {
  description = "Daily cost threshold for alarms"
  type        = number
  default     = 100
}

variable "monthly_cost_threshold" {
  description = "Monthly cost threshold for alarms"
  type        = number
  default     = 2000
}

variable "ec2_cost_threshold" {
  description = "EC2 cost threshold for alarms"
  type        = number
  default     = 200
}

# SNS topics
variable "create_sns_topics" {
  description = "Whether to create SNS topics"
  type        = bool
  default     = true
}

# Cost allocation tags
variable "create_cost_allocation_tags" {
  description = "Whether to create cost allocation tags"
  type        = bool
  default     = true
}

# Anomaly detection
variable "create_anomaly_detection" {
  description = "Whether to create cost anomaly detection"
  type        = bool
  default     = true
}

# Dashboards
variable "create_dashboards" {
  description = "Whether to create CloudWatch dashboards"
  type        = bool
  default     = true
}

# Lambda functions
variable "create_lambda_functions" {
  description = "Whether to create Lambda functions"
  type        = bool
  default     = true
}

# EventBridge rules
variable "create_eventbridge_rules" {
  description = "Whether to create EventBridge rules"
  type        = bool
  default     = true
}

# S3 bucket
variable "create_s3_bucket" {
  description = "Whether to create S3 bucket for reports"
  type        = bool
  default     = true
}

# Cost and usage report
variable "create_cost_usage_report" {
  description = "Whether to create Cost and Usage Report"
  type        = bool
  default     = true
}

# Logging
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

# Cost optimization settings
variable "enable_auto_scaling" {
  description = "Enable auto-scaling for cost optimization"
  type        = bool
  default     = true
}

variable "enable_spot_instances" {
  description = "Enable Spot instances for cost savings"
  type        = bool
  default     = true
}

variable "enable_reserved_instances" {
  description = "Enable Reserved Instance recommendations"
  type        = bool
  default     = true
}

variable "enable_savings_plans" {
  description = "Enable Savings Plans recommendations"
  type        = bool
  default     = true
}

# Monitoring settings
variable "enable_detailed_monitoring" {
  description = "Enable detailed cost monitoring"
  type        = bool
  default     = true
}

variable "monitoring_retention_days" {
  description = "Monitoring data retention in days"
  type        = number
  default     = 30
}

# Alerting thresholds
variable "cost_alert_thresholds" {
  description = "Cost alert thresholds as percentages"
  type        = list(number)
  default     = [80, 90, 100]
}

variable "anomaly_detection_threshold" {
  description = "Anomaly detection threshold"
  type        = number
  default     = 0.1
}

# Cost categories
variable "cost_categories" {
  description = "Cost categories for allocation"
  type        = list(string)
  default     = ["Environment", "Project", "Component", "CostCenter", "Owner"]
}

# Service-specific monitoring
variable "monitored_services" {
  description = "Services to monitor for costs"
  type        = list(string)
  default     = [
    "Amazon Elastic Compute Cloud - Compute",
    "Amazon Simple Storage Service",
    "Amazon Relational Database Service",
    "AWS Lambda",
    "Amazon Elastic Block Store",
    "Amazon CloudFront",
    "Amazon API Gateway"
  ]
}

# Budget notification settings
variable "budget_notification_thresholds" {
  description = "Budget notification thresholds"
  type        = list(number)
  default     = [50, 80, 100]
}

variable "budget_notification_types" {
  description = "Budget notification types"
  type        = list(string)
  default     = ["ACTUAL", "FORECASTED"]
}

# Cost optimization automation
variable "enable_cost_automation" {
  description = "Enable cost optimization automation"
  type        = bool
  default     = true
}

variable "automation_schedule" {
  description = "Schedule for cost automation"
  type        = map(string)
  default = {
    daily_check    = "cron(0 9 * * ? *)"    # 9 AM UTC daily
    weekly_report  = "cron(0 10 ? * MON *)" # 10 AM UTC Monday
    monthly_opt    = "cron(0 11 1 * ? *)"   # 11 AM UTC 1st of month
    cleanup        = "cron(0 2 ? * SUN *)"  # 2 AM UTC Sunday
  }
}

# Resource tagging
variable "enable_auto_tagging" {
  description = "Enable automatic resource tagging"
  type        = bool
  default     = true
}

variable "required_tags" {
  description = "Required tags for cost allocation"
  type        = list(string)
  default     = ["Environment", "Project", "Component", "Owner", "CostCenter"]
}

# Cost reporting
variable "report_frequency" {
  description = "Cost report frequency"
  type        = string
  default     = "daily"
  validation {
    condition     = contains(["daily", "weekly", "monthly"], var.report_frequency)
    error_message = "Report frequency must be daily, weekly, or monthly."
  }
}

variable "report_formats" {
  description = "Cost report formats"
  type        = list(string)
  default     = ["csv", "json"]
}

# Cost optimization policies
variable "optimization_policies" {
  description = "Cost optimization policies"
  type = map(object({
    enabled                = bool
    threshold_percentage   = number
    action_type           = string
    notification_required = bool
  }))
  default = {
    rightsizing = {
      enabled                = true
      threshold_percentage   = 70
      action_type           = "recommendation"
      notification_required = true
    }
    reserved_instances = {
      enabled                = true
      threshold_percentage   = 80
      action_type           = "recommendation"
      notification_required = true
    }
    savings_plans = {
      enabled                = true
      threshold_percentage   = 80
      action_type           = "recommendation"
      notification_required = true
    }
    unused_resources = {
      enabled                = true
      threshold_percentage   = 0
      action_type           = "cleanup"
      notification_required = true
    }
  }
}

# Cost governance rules
variable "governance_rules" {
  description = "Cost governance rules"
  type = map(object({
    enabled     = bool
    threshold   = number
    action      = string
    description = string
  }))
  default = {
    high_cost_alert = {
      enabled     = true
      threshold   = 1000
      action      = "alert"
      description = "Alert when daily cost exceeds $1000"
    }
    budget_exceeded = {
      enabled     = true
      threshold   = 100
      action      = "block"
      description = "Block resources when budget exceeded"
    }
    untagged_resources = {
      enabled     = true
      threshold   = 0
      action      = "alert"
      description = "Alert on untagged resources"
    }
  }
}

# Cost allocation methods
variable "allocation_methods" {
  description = "Cost allocation methods"
  type        = list(string)
  default     = ["tag", "service", "account", "region"]
}

# Cost optimization targets
variable "optimization_targets" {
  description = "Cost optimization targets"
  type = map(object({
    target_percentage = number
    timeframe_days    = number
    priority          = string
  }))
  default = {
    ec2_optimization = {
      target_percentage = 20
      timeframe_days    = 30
      priority          = "high"
    }
    storage_optimization = {
      target_percentage = 15
      timeframe_days    = 60
      priority          = "medium"
    }
    database_optimization = {
      target_percentage = 25
      timeframe_days    = 45
      priority          = "high"
    }
  }
}

# Custom tags
variable "custom_tags" {
  description = "Custom tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Feature flags
variable "feature_flags" {
  description = "Feature flags for cost governance"
  type        = map(bool)
  default = {
    enable_anomaly_detection    = true
    enable_rightsizing          = true
    enable_reserved_instances   = true
    enable_savings_plans        = true
    enable_spot_instances       = true
    enable_auto_scaling         = true
    enable_cost_allocation      = true
    enable_budget_alerts        = true
    enable_cost_forecasting     = true
    enable_optimization_reports = true
  }
}