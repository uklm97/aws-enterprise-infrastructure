output "primary_region" {
  description = "Primary AWS region"
  value       = var.primary_region
}

output "secondary_regions" {
  description = "Secondary AWS regions"
  value       = var.secondary_regions
}

output "s3_buckets" {
  description = "S3 buckets across regions"
  value = {
    primary = {
      name = aws_s3_bucket.primary_bucket.bucket
      arn  = aws_s3_bucket.primary_bucket.arn
      region = var.primary_region
    }
    secondary = {
      name = aws_s3_bucket.secondary_bucket.bucket
      arn  = aws_s3_bucket.secondary_bucket.arn
      region = var.secondary_regions[0]
    }
    tertiary = {
      name = aws_s3_bucket.tertiary_bucket.bucket
      arn  = aws_s3_bucket.tertiary_bucket.arn
      region = var.secondary_regions[1]
    }
  }
}

output "dynamodb_global_table" {
  description = "DynamoDB global table"
  value = {
    name = aws_dynamodb_table.global_table.name
    arn  = aws_dynamodb_table.global_table.arn
    regions = [var.primary_region] + var.secondary_regions
  }
}

output "rds_instances" {
  description = "RDS instances across regions"
  value = {
    primary = {
      identifier = aws_db_instance.primary_db.identifier
      endpoint   = aws_db_instance.primary_db.endpoint
      region     = var.primary_region
    }
    secondary = {
      identifier = aws_db_instance.secondary_db.identifier
      endpoint   = aws_db_instance.secondary_db.endpoint
      region     = var.secondary_regions[0]
    }
    tertiary = {
      identifier = aws_db_instance.tertiary_db.identifier
      endpoint   = aws_db_instance.tertiary_db.endpoint
      region     = var.secondary_regions[1]
    }
  }
}

output "vpc_networks" {
  description = "VPC networks across regions"
  value = {
    primary = {
      vpc_id = aws_vpc.primary_vpc.id
      cidr_block = aws_vpc.primary_vpc.cidr_block
      region = var.primary_region
    }
    secondary = {
      vpc_id = aws_vpc.secondary_vpc.id
      cidr_block = aws_vpc.secondary_vpc.cidr_block
      region = var.secondary_regions[0]
    }
    tertiary = {
      vpc_id = aws_vpc.tertiary_vpc.id
      cidr_block = aws_vpc.tertiary_vpc.cidr_block
      region = var.secondary_regions[1]
    }
  }
}

output "cloudfront_distribution" {
  description = "CloudFront distribution"
  value = {
    id = aws_cloudfront_distribution.global_distribution.id
    domain_name = aws_cloudfront_distribution.global_distribution.domain_name
    hosted_zone_id = aws_cloudfront_distribution.global_distribution.hosted_zone_id
    status = aws_cloudfront_distribution.global_distribution.status
  }
}

output "route53_zone" {
  description = "Route53 hosted zone"
  value = {
    zone_id = aws_route53_zone.main.zone_id
    name_servers = aws_route53_zone.main.name_servers
    domain_name = var.domain_name
  }
}

output "route53_health_checks" {
  description = "Route53 health checks"
  value = {
    primary = {
      id = aws_route53_health_check.primary.id
      fqdn = aws_route53_health_check.primary.fqdn
    }
    secondary = {
      id = aws_route53_health_check.secondary.id
      fqdn = aws_route53_health_check.secondary.fqdn
    }
  }
}

output "kms_key" {
  description = "KMS key for encryption"
  value = {
    id = aws_kms_key.multi_region_encryption.key_id
    arn = aws_kms_key.multi_region_encryption.arn
    region = var.primary_region
  }
}

output "replication_role" {
  description = "IAM role for S3 replication"
  value = {
    name = aws_iam_role.replication_role.name
    arn = aws_iam_role.replication_role.arn
  }
}

output "multi_region_capabilities" {
  description = "Available multi-region capabilities"
  value = {
    cross_region_replication = "S3 cross-region replication enabled"
    global_distribution = "CloudFront global distribution enabled"
    disaster_recovery = "Automated disaster recovery enabled"
    health_monitoring = "Cross-region health monitoring enabled"
    automated_failover = "Route53 automated failover enabled"
    data_synchronization = "DynamoDB global tables enabled"
    global_load_balancing = "Multi-region load balancing enabled"
    edge_caching = "CloudFront edge caching enabled"
    dns_failover = "Route53 DNS failover enabled"
    backup_replication = "Cross-region backup replication enabled"
  }
}

output "architecture_summary" {
  description = "Multi-region architecture summary"
  value = {
    primary_region = var.primary_region
    secondary_regions = var.secondary_regions
    total_regions = 1 + length(var.secondary_regions)
    rto_minutes = var.rto_minutes
    rpo_minutes = var.rpo_minutes
    features_enabled = {
      cross_region_replication = var.enable_cross_region_replication
      global_distribution = var.enable_global_distribution
      disaster_recovery = var.enable_disaster_recovery
      health_monitoring = var.enable_health_monitoring
      automated_failover = var.enable_automated_failover
    }
  }
}

output "monitoring_endpoints" {
  description = "Monitoring and management endpoints"
  value = {
    cloudwatch_console = "https://console.aws.amazon.com/cloudwatch/home"
    route53_console = "https://console.aws.amazon.com/route53/home"
    s3_console = "https://console.aws.amazon.com/s3/home"
    rds_console = "https://console.aws.amazon.com/rds/home"
    dynamodb_console = "https://console.aws.amazon.com/dynamodb/home"
    cloudfront_console = "https://console.aws.amazon.com/cloudfront/home"
  }
}

output "next_steps" {
  description = "Recommended next steps for multi-region architecture"
  value = [
    "1. Configure DNS records to point to your domain",
    "2. Set up monitoring and alerting for all regions",
    "3. Test disaster recovery procedures",
    "4. Configure cross-region backup policies",
    "5. Set up automated failover testing",
    "6. Configure compliance monitoring",
    "7. Set up cost optimization policies",
    "8. Configure security monitoring",
    "9. Set up performance monitoring",
    "10. Test global load balancing"
  ]
}

output "disaster_recovery_info" {
  description = "Disaster recovery information"
  value = {
    rto_minutes = var.rto_minutes
    rpo_minutes = var.rpo_minutes
    failover_threshold = var.failover_threshold
    health_check_interval = var.health_check_interval
    backup_retention_days = var.backup_retention_days
    dr_test_schedule = var.dr_test_schedule
  }
}

output "security_info" {
  description = "Security configuration information"
  value = {
    encryption_enabled = var.enable_encryption
    vpc_flow_logs_enabled = var.enable_vpc_flow_logs
    cloudtrail_enabled = var.enable_cloudtrail
    config_enabled = var.enable_config
    kms_key_id = aws_kms_key.multi_region_encryption.key_id
  }
}

output "performance_info" {
  description = "Performance configuration information"
  value = {
    caching_enabled = var.enable_caching
    cache_ttl = var.cache_ttl
    compression_enabled = var.enable_compression
    http2_enabled = var.enable_http2
    auto_scaling_enabled = var.enable_auto_scaling
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
    target_capacity = var.target_capacity
  }
}

output "cost_optimization_info" {
  description = "Cost optimization information"
  value = {
    spot_instances_enabled = var.enable_spot_instances
    reserved_instances_enabled = var.enable_reserved_instances
    auto_scaling_enabled = var.enable_auto_scaling
    max_instances_per_region = var.max_instances_per_region
    max_storage_per_region = var.max_storage_per_region
    max_bandwidth_per_region = var.max_bandwidth_per_region
  }
}

output "compliance_info" {
  description = "Compliance configuration information"
  value = {
    compliance_monitoring_enabled = var.enable_compliance_monitoring
    compliance_frameworks = var.compliance_frameworks
    data_retention_days = var.data_retention_days
    audit_log_retention_days = var.audit_log_retention_days
  }
}

output "network_info" {
  description = "Network configuration information"
  value = {
    vpc_peering_enabled = var.enable_vpc_peering
    transit_gateway_enabled = var.enable_transit_gateway
    direct_connect_enabled = var.enable_direct_connect
    primary_vpc_cidr = var.primary_vpc_cidr
    secondary_vpc_cidr = var.secondary_vpc_cidr
    tertiary_vpc_cidr = var.tertiary_vpc_cidr
  }
}

output "backup_info" {
  description = "Backup configuration information"
  value = {
    backup_retention_days = var.backup_retention_days
    backup_schedule = var.backup_schedule
    cross_region_backup_enabled = var.enable_cross_region_backup
  }
}

output "monitoring_info" {
  description = "Monitoring configuration information"
  value = {
    detailed_monitoring_enabled = var.enable_detailed_monitoring
    monitoring_retention_days = var.monitoring_retention_days
    log_retention_days = var.log_retention_days
    xray_tracing_enabled = var.enable_xray_tracing
    cloudwatch_alarms_enabled = var.enable_cloudwatch_alarms
    sns_notifications_enabled = var.enable_sns_notifications
  }
}

output "development_info" {
  description = "Development environment information"
  value = {
    dev_environment_enabled = var.enable_dev_environment
    test_environment_enabled = var.enable_test_environment
    staging_environment_enabled = var.enable_staging_environment
  }
}

output "dr_testing_info" {
  description = "Disaster recovery testing information"
  value = {
    dr_testing_enabled = var.enable_dr_testing
    dr_test_schedule = var.dr_test_schedule
    dr_test_duration_hours = var.dr_test_duration_hours
  }
}

output "global_tags" {
  description = "Global tags applied to all resources"
  value = var.global_tags
}

output "feature_flags" {
  description = "Feature flags status"
  value = var.feature_flags
}

output "resource_limits" {
  description = "Resource limits configuration"
  value = {
    max_instances_per_region = var.max_instances_per_region
    max_storage_per_region = var.max_storage_per_region
    max_bandwidth_per_region = var.max_bandwidth_per_region
  }
}

output "alarm_thresholds" {
  description = "CloudWatch alarm thresholds"
  value = {
    cpu_threshold = var.alarm_threshold_cpu
    memory_threshold = var.alarm_threshold_memory
    disk_threshold = var.alarm_threshold_disk
  }
}

output "notification_config" {
  description = "Notification configuration"
  value = {
    email = var.notification_email
    sns_enabled = var.enable_sns_notifications
    cloudwatch_alarms_enabled = var.enable_cloudwatch_alarms
  }
}