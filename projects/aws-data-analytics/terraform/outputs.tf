# AWS Data & Analytics Platform - Outputs
# This file defines all the output values for the Terraform configuration

# S3 Data Lake Outputs
output "data_lake_bucket_name" {
  description = "Name of the S3 bucket for data lake"
  value       = aws_s3_bucket.data_lake.bucket
}

output "data_lake_bucket_arn" {
  description = "ARN of the S3 bucket for data lake"
  value       = aws_s3_bucket.data_lake.arn
}

output "data_lake_bucket_domain_name" {
  description = "Domain name of the S3 bucket for data lake"
  value       = aws_s3_bucket.data_lake.bucket_domain_name
}

# Glue Data Catalog Outputs
output "glue_database_name" {
  description = "Name of the Glue database"
  value       = aws_glue_catalog_database.data_lake.name
}

output "glue_database_arn" {
  description = "ARN of the Glue database"
  value       = aws_glue_catalog_database.data_lake.arn
}

output "glue_crawler_name" {
  description = "Name of the Glue crawler"
  value       = aws_glue_crawler.data_lake.name
}

output "glue_crawler_arn" {
  description = "ARN of the Glue crawler"
  value       = aws_glue_crawler.data_lake.arn
}

# Redshift Outputs
output "redshift_cluster_id" {
  description = "Redshift cluster identifier"
  value       = aws_redshift_cluster.main.cluster_identifier
}

output "redshift_cluster_arn" {
  description = "ARN of the Redshift cluster"
  value       = aws_redshift_cluster.main.arn
}

output "redshift_cluster_endpoint" {
  description = "Redshift cluster endpoint"
  value       = aws_redshift_cluster.main.endpoint
}

output "redshift_cluster_port" {
  description = "Redshift cluster port"
  value       = aws_redshift_cluster.main.port
}

output "redshift_cluster_database_name" {
  description = "Redshift cluster database name"
  value       = aws_redshift_cluster.main.database_name
}

output "redshift_cluster_master_username" {
  description = "Redshift cluster master username"
  value       = aws_redshift_cluster.main.master_username
  sensitive   = true
}

# Kinesis Outputs
output "kinesis_stream_name" {
  description = "Name of the Kinesis data stream"
  value       = aws_kinesis_stream.main.name
}

output "kinesis_stream_arn" {
  description = "ARN of the Kinesis data stream"
  value       = aws_kinesis_stream.main.arn
}

output "kinesis_stream_shard_count" {
  description = "Number of shards in the Kinesis stream"
  value       = aws_kinesis_stream.main.shard_count
}

output "kinesis_firehose_name" {
  description = "Name of the Kinesis Data Firehose"
  value       = aws_kinesis_firehose_delivery_stream.main.name
}

output "kinesis_firehose_arn" {
  description = "ARN of the Kinesis Data Firehose"
  value       = aws_kinesis_firehose_delivery_stream.main.arn
}

# SageMaker Outputs
output "sagemaker_notebook_instance_name" {
  description = "Name of the SageMaker notebook instance"
  value       = var.create_sagemaker_notebook ? aws_sagemaker_notebook_instance.main[0].name : null
}

output "sagemaker_notebook_instance_arn" {
  description = "ARN of the SageMaker notebook instance"
  value       = var.create_sagemaker_notebook ? aws_sagemaker_notebook_instance.main[0].arn : null
}

output "sagemaker_notebook_instance_url" {
  description = "URL of the SageMaker notebook instance"
  value       = var.create_sagemaker_notebook ? aws_sagemaker_notebook_instance.main[0].url : null
}

# KMS Outputs
output "kinesis_kms_key_id" {
  description = "ID of the KMS key for Kinesis"
  value       = aws_kms_key.kinesis.key_id
}

output "kinesis_kms_key_arn" {
  description = "ARN of the KMS key for Kinesis"
  value       = aws_kms_key.kinesis.arn
}

output "kinesis_kms_alias_name" {
  description = "Name of the KMS alias for Kinesis"
  value       = aws_kms_alias.kinesis.name
}

# CloudWatch Logs Outputs
output "data_analytics_log_group_name" {
  description = "Name of the CloudWatch log group for data analytics"
  value       = aws_cloudwatch_log_group.data_analytics.name
}

output "data_analytics_log_group_arn" {
  description = "ARN of the CloudWatch log group for data analytics"
  value       = aws_cloudwatch_log_group.data_analytics.arn
}

output "firehose_log_group_name" {
  description = "Name of the CloudWatch log group for Firehose"
  value       = aws_cloudwatch_log_group.firehose.name
}

output "firehose_log_group_arn" {
  description = "ARN of the CloudWatch log group for Firehose"
  value       = aws_cloudwatch_log_group.firehose.arn
}

# CloudWatch Alarms Outputs
output "kinesis_incoming_records_alarm_name" {
  description = "Name of the Kinesis incoming records CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.kinesis_incoming_records[0].alarm_name : null
}

output "kinesis_incoming_records_alarm_arn" {
  description = "ARN of the Kinesis incoming records CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.kinesis_incoming_records[0].arn : null
}

output "redshift_cpu_utilization_alarm_name" {
  description = "Name of the Redshift CPU utilization CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.redshift_cpu_utilization[0].alarm_name : null
}

output "redshift_cpu_utilization_alarm_arn" {
  description = "ARN of the Redshift CPU utilization CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.redshift_cpu_utilization[0].arn : null
}

# IAM Role Outputs
output "glue_crawler_role_arn" {
  description = "ARN of the Glue crawler IAM role"
  value       = aws_iam_role.glue_crawler_role.arn
}

output "firehose_role_arn" {
  description = "ARN of the Firehose IAM role"
  value       = aws_iam_role.firehose_role.arn
}

output "sagemaker_role_arn" {
  description = "ARN of the SageMaker IAM role"
  value       = aws_iam_role.sagemaker_role.arn
}

# General Information
output "aws_region" {
  description = "AWS region where resources are created"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "project_name" {
  description = "Name of the project"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Connection Information
output "redshift_connection_info" {
  description = "Redshift connection information"
  value = {
    endpoint = aws_redshift_cluster.main.endpoint
    port     = aws_redshift_cluster.main.port
    database = aws_redshift_cluster.main.database_name
    username = aws_redshift_cluster.main.master_username
  }
  sensitive = true
}

output "kinesis_connection_info" {
  description = "Kinesis connection information"
  value = {
    stream_name = aws_kinesis_stream.main.name
    stream_arn  = aws_kinesis_stream.main.arn
    shard_count = aws_kinesis_stream.main.shard_count
  }
}

output "s3_connection_info" {
  description = "S3 connection information"
  value = {
    bucket_name = aws_s3_bucket.data_lake.bucket
    bucket_arn  = aws_s3_bucket.data_lake.arn
    region      = var.aws_region
  }
}