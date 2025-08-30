variable "aws_region" {
  description = "AWS region for the audit framework"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-audit-framework"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Security Audit Variables
variable "enable_iam_analysis" {
  description = "Enable IAM analysis"
  type        = bool
  default     = true
}

variable "enable_security_groups" {
  description = "Enable security group analysis"
  type        = bool
  default     = true
}

variable "enable_vpc_audit" {
  description = "Enable VPC configuration audit"
  type        = bool
  default     = true
}

variable "enable_encryption_audit" {
  description = "Enable encryption status audit"
  type        = bool
  default     = true
}

# Cost Audit Variables
variable "enable_cost_analysis" {
  description = "Enable cost analysis"
  type        = bool
  default     = true
}

variable "enable_budget_alerts" {
  description = "Enable budget alerts"
  type        = bool
  default     = true
}

variable "enable_utilization_audit" {
  description = "Enable resource utilization audit"
  type        = bool
  default     = true
}

# Performance Audit Variables
variable "enable_performance_monitoring" {
  description = "Enable performance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_dashboards" {
  description = "Enable CloudWatch dashboards"
  type        = bool
  default     = true
}

variable "enable_alerts" {
  description = "Enable performance alerts"
  type        = bool
  default     = true
}

# Compliance Audit Variables
variable "enable_config_rules" {
  description = "Enable AWS Config rules"
  type        = bool
  default     = true
}

variable "enable_cis_benchmarks" {
  description = "Enable CIS benchmark compliance checks"
  type        = bool
  default     = true
}

variable "enable_compliance_alerts" {
  description = "Enable compliance alerts"
  type        = bool
  default     = true
}

# Logging and Monitoring Variables
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

variable "audit_schedule" {
  description = "Cron expression for audit schedule"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM UTC
}

# Alerting Variables
variable "enable_email_alerts" {
  description = "Enable email alerts"
  type        = bool
  default     = true
}

variable "alert_email_address" {
  description = "Email address for alerts"
  type        = string
  default     = "admin@example.com"
}

variable "cost_threshold" {
  description = "Cost threshold for alerts (USD)"
  type        = number
  default     = 1000
}

# Security Configuration Variables
variable "enable_mfa_enforcement" {
  description = "Enable MFA enforcement"
  type        = bool
  default     = true
}

variable "enable_password_policy" {
  description = "Enable password policy enforcement"
  type        = bool
  default     = true
}

variable "minimum_password_length" {
  description = "Minimum password length"
  type        = number
  default     = 12
}

variable "password_require_symbols" {
  description = "Require symbols in passwords"
  type        = bool
  default     = true
}

variable "password_require_numbers" {
  description = "Require numbers in passwords"
  type        = bool
  default     = true
}

variable "password_require_uppercase" {
  description = "Require uppercase letters in passwords"
  type        = bool
  default     = true
}

variable "password_require_lowercase" {
  description = "Require lowercase letters in passwords"
  type        = bool
  default     = true
}

variable "password_expire_passwords" {
  description = "Enable password expiration"
  type        = bool
  default     = true
}

variable "password_max_age" {
  description = "Maximum password age in days"
  type        = number
  default     = 90
}

variable "password_reuse_prevention" {
  description = "Number of passwords to prevent reuse"
  type        = number
  default     = 5
}

# Compliance Configuration Variables
variable "enable_guardduty" {
  description = "Enable GuardDuty"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable Security Hub"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config"
  type        = bool
  default     = true
}

# Cost Optimization Variables
variable "enable_reserved_instance_analysis" {
  description = "Enable Reserved Instance analysis"
  type        = bool
  default     = true
}

variable "enable_spot_instance_analysis" {
  description = "Enable Spot Instance analysis"
  type        = bool
  default     = true
}

variable "enable_unused_resource_analysis" {
  description = "Enable unused resource analysis"
  type        = bool
  default     = true
}

# Performance Monitoring Variables
variable "enable_cpu_monitoring" {
  description = "Enable CPU monitoring"
  type        = bool
  default     = true
}

variable "enable_memory_monitoring" {
  description = "Enable memory monitoring"
  type        = bool
  default     = true
}

variable "enable_network_monitoring" {
  description = "Enable network monitoring"
  type        = bool
  default     = true
}

variable "enable_disk_monitoring" {
  description = "Enable disk monitoring"
  type        = bool
  default     = true
}

# Reporting Variables
variable "enable_html_reports" {
  description = "Enable HTML report generation"
  type        = bool
  default     = true
}

variable "enable_pdf_reports" {
  description = "Enable PDF report generation"
  type        = bool
  default     = true
}

variable "enable_json_reports" {
  description = "Enable JSON report generation"
  type        = bool
  default     = true
}

variable "enable_csv_reports" {
  description = "Enable CSV report generation"
  type        = bool
  default     = true
}

# Tags
variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Project     = "aws-audit-framework"
    Environment = "production"
    ManagedBy   = "Terraform"
    Purpose     = "Infrastructure Audit"
  }
}
