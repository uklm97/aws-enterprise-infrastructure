variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_regions" {
  description = "Secondary AWS regions"
  type        = list(string)
  default     = ["us-west-2", "eu-west-1"]
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "aws-multi-region"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "example.com"
}

# VPC Configuration
variable "primary_vpc_cidr" {
  description = "CIDR block for primary VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "secondary_vpc_cidr" {
  description = "CIDR block for secondary VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "tertiary_vpc_cidr" {
  description = "CIDR block for tertiary VPC"
  type        = string
  default     = "10.2.0.0/16"
}

# Subnet Configuration
variable "primary_public_subnet_1_cidr" {
  description = "CIDR block for primary public subnet 1"
  type        = string
  default     = "10.0.1.0/24"
}

variable "primary_public_subnet_2_cidr" {
  description = "CIDR block for primary public subnet 2"
  type        = string
  default     = "10.0.2.0/24"
}

variable "primary_private_subnet_1_cidr" {
  description = "CIDR block for primary private subnet 1"
  type        = string
  default     = "10.0.3.0/24"
}

variable "primary_private_subnet_2_cidr" {
  description = "CIDR block for primary private subnet 2"
  type        = string
  default     = "10.0.4.0/24"
}

variable "secondary_public_subnet_1_cidr" {
  description = "CIDR block for secondary public subnet 1"
  type        = string
  default     = "10.1.1.0/24"
}

variable "secondary_public_subnet_2_cidr" {
  description = "CIDR block for secondary public subnet 2"
  type        = string
  default     = "10.1.2.0/24"
}

variable "secondary_private_subnet_1_cidr" {
  description = "CIDR block for secondary private subnet 1"
  type        = string
  default     = "10.1.3.0/24"
}

variable "secondary_private_subnet_2_cidr" {
  description = "CIDR block for secondary private subnet 2"
  type        = string
  default     = "10.1.4.0/24"
}

variable "tertiary_public_subnet_1_cidr" {
  description = "CIDR block for tertiary public subnet 1"
  type        = string
  default     = "10.2.1.0/24"
}

variable "tertiary_public_subnet_2_cidr" {
  description = "CIDR block for tertiary public subnet 2"
  type        = string
  default     = "10.2.2.0/24"
}

variable "tertiary_private_subnet_1_cidr" {
  description = "CIDR block for tertiary private subnet 1"
  type        = string
  default     = "10.2.3.0/24"
}

variable "tertiary_private_subnet_2_cidr" {
  description = "CIDR block for tertiary private subnet 2"
  type        = string
  default     = "10.2.4.0/24"
}

# Database Configuration
variable "db_engine" {
  description = "Database engine"
  type        = string
  default     = "mysql"
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "8.0"
}

variable "db_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Database allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_storage_type" {
  description = "Database storage type"
  type        = string
  default     = "gp2"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "mydb"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "changeme123"
}

variable "db_backup_retention_period" {
  description = "Database backup retention period in days"
  type        = number
  default     = 7
}

variable "db_backup_window" {
  description = "Database backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "db_maintenance_window" {
  description = "Database maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "db_skip_final_snapshot" {
  description = "Skip final snapshot when destroying database"
  type        = bool
  default     = true
}

variable "db_deletion_protection" {
  description = "Enable deletion protection for database"
  type        = bool
  default     = false
}

# Multi-Region Features
variable "enable_cross_region_replication" {
  description = "Enable cross-region replication"
  type        = bool
  default     = true
}

variable "enable_global_distribution" {
  description = "Enable global distribution with CloudFront"
  type        = bool
  default     = true
}

variable "enable_disaster_recovery" {
  description = "Enable disaster recovery features"
  type        = bool
  default     = true
}

variable "enable_health_monitoring" {
  description = "Enable health monitoring across regions"
  type        = bool
  default     = true
}

variable "enable_automated_failover" {
  description = "Enable automated failover"
  type        = bool
  default     = true
}

# Disaster Recovery Configuration
variable "rto_minutes" {
  description = "Recovery Time Objective in minutes"
  type        = number
  default     = 60
}

variable "rpo_minutes" {
  description = "Recovery Point Objective in minutes"
  type        = number
  default     = 15
}

variable "failover_threshold" {
  description = "Failover threshold for health checks"
  type        = number
  default     = 3
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

# Monitoring Configuration
variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "enable_sns_notifications" {
  description = "Enable SNS notifications"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for notifications"
  type        = string
  default     = ""
}

variable "alarm_threshold_cpu" {
  description = "CPU utilization alarm threshold"
  type        = number
  default     = 80
}

variable "alarm_threshold_memory" {
  description = "Memory utilization alarm threshold"
  type        = number
  default     = 80
}

variable "alarm_threshold_disk" {
  description = "Disk utilization alarm threshold"
  type        = number
  default     = 80
}

# Security Configuration
variable "enable_encryption" {
  description = "Enable encryption for all resources"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail logging"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "enable_reserved_instances" {
  description = "Enable reserved instances for cost optimization"
  type        = bool
  default     = false
}

variable "enable_auto_scaling" {
  description = "Enable auto scaling"
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

variable "target_capacity" {
  description = "Target capacity for auto scaling"
  type        = number
  default     = 3
}

# Performance Configuration
variable "enable_caching" {
  description = "Enable caching for performance"
  type        = bool
  default     = true
}

variable "cache_ttl" {
  description = "Cache TTL in seconds"
  type        = number
  default     = 3600
}

variable "enable_compression" {
  description = "Enable compression for performance"
  type        = bool
  default     = true
}

variable "enable_http2" {
  description = "Enable HTTP/2 for performance"
  type        = bool
  default     = true
}

# Compliance Configuration
variable "enable_compliance_monitoring" {
  description = "Enable compliance monitoring"
  type        = bool
  default     = true
}

variable "compliance_frameworks" {
  description = "Compliance frameworks to implement"
  type        = list(string)
  default     = ["SOC2", "HIPAA", "PCI-DSS"]
}

variable "data_retention_days" {
  description = "Data retention period in days"
  type        = number
  default     = 90
}

variable "audit_log_retention_days" {
  description = "Audit log retention period in days"
  type        = number
  default     = 365
}

# Custom Tags
variable "custom_tags" {
  description = "Custom tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Feature Flags
variable "feature_flags" {
  description = "Feature flags for multi-region architecture"
  type        = map(bool)
  default = {
    enable_multi_region_replication = true
    enable_global_distribution      = true
    enable_disaster_recovery        = true
    enable_health_monitoring        = true
    enable_automated_failover       = true
    enable_cross_region_backup      = true
    enable_global_load_balancing    = true
    enable_edge_caching             = true
    enable_dns_failover             = true
    enable_data_synchronization     = true
  }
}

# Network Configuration
variable "enable_vpc_peering" {
  description = "Enable VPC peering between regions"
  type        = bool
  default     = false
}

variable "enable_transit_gateway" {
  description = "Enable Transit Gateway for multi-region connectivity"
  type        = bool
  default     = false
}

variable "enable_direct_connect" {
  description = "Enable Direct Connect for hybrid connectivity"
  type        = bool
  default     = false
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "backup_schedule" {
  description = "Backup schedule (cron expression)"
  type        = string
  default     = "0 2 * * *"  # Daily at 2 AM
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup"
  type        = bool
  default     = true
}

# Monitoring and Alerting
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

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 14
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing"
  type        = bool
  default     = true
}

# Development and Testing
variable "enable_dev_environment" {
  description = "Enable development environment"
  type        = bool
  default     = false
}

variable "enable_test_environment" {
  description = "Enable test environment"
  type        = bool
  default     = false
}

variable "enable_staging_environment" {
  description = "Enable staging environment"
  type        = bool
  default     = false
}

# Disaster Recovery Testing
variable "enable_dr_testing" {
  description = "Enable disaster recovery testing"
  type        = bool
  default     = true
}

variable "dr_test_schedule" {
  description = "DR test schedule (cron expression)"
  type        = string
  default     = "0 0 1 * *"  # Monthly on the 1st
}

variable "dr_test_duration_hours" {
  description = "DR test duration in hours"
  type        = number
  default     = 4
}

# Global Configuration
variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "aws-multi-region"
    Environment = "dev"
    ManagedBy   = "Terraform"
    Owner       = "DevOps Team"
    CostCenter  = "Engineering"
  }
}

# Resource Limits
variable "max_instances_per_region" {
  description = "Maximum number of instances per region"
  type        = number
  default     = 10
}

variable "max_storage_per_region" {
  description = "Maximum storage per region in GB"
  type        = number
  default     = 1000
}

variable "max_bandwidth_per_region" {
  description = "Maximum bandwidth per region in Mbps"
  type        = number
  default     = 1000
}