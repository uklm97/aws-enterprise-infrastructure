# AWS CI/CD & DevOps Platform - Outputs
# This file defines all the output values for the Terraform configuration

# S3 Buckets
output "pipeline_artifacts_bucket" {
  description = "S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.pipeline_artifacts.bucket
}

output "pipeline_artifacts_bucket_arn" {
  description = "ARN of the S3 bucket for CodePipeline artifacts"
  value       = aws_s3_bucket.pipeline_artifacts.arn
}

output "build_cache_bucket" {
  description = "S3 bucket for CodeBuild cache"
  value       = aws_s3_bucket.build_cache.bucket
}

output "build_cache_bucket_arn" {
  description = "ARN of the S3 bucket for CodeBuild cache"
  value       = aws_s3_bucket.build_cache.arn
}

# IAM Roles
output "codepipeline_role_arn" {
  description = "ARN of the CodePipeline IAM role"
  value       = aws_iam_role.codepipeline_role.arn
}

output "codebuild_role_arn" {
  description = "ARN of the CodeBuild IAM role"
  value       = aws_iam_role.codebuild_role.arn
}

output "codedeploy_role_arn" {
  description = "ARN of the CodeDeploy IAM role"
  value       = aws_iam_role.codedeploy_role.arn
}

# CloudWatch Log Groups
output "pipeline_log_group_name" {
  description = "Name of the CodePipeline CloudWatch log group"
  value       = aws_cloudwatch_log_group.pipeline_logs.name
}

output "pipeline_log_group_arn" {
  description = "ARN of the CodePipeline CloudWatch log group"
  value       = aws_cloudwatch_log_group.pipeline_logs.arn
}

output "build_log_group_name" {
  description = "Name of the CodeBuild CloudWatch log group"
  value       = aws_cloudwatch_log_group.build_logs.name
}

output "build_log_group_arn" {
  description = "ARN of the CodeBuild CloudWatch log group"
  value       = aws_cloudwatch_log_group.build_logs.arn
}

# CodeBuild Projects
output "build_project_name" {
  description = "Name of the CodeBuild project"
  value       = var.create_build_project ? aws_codebuild_project.build_project[0].name : null
}

output "build_project_arn" {
  description = "ARN of the CodeBuild project"
  value       = var.create_build_project ? aws_codebuild_project.build_project[0].arn : null
}

output "test_project_name" {
  description = "Name of the test CodeBuild project"
  value       = var.create_test_project ? aws_codebuild_project.test_project[0].name : null
}

output "test_project_arn" {
  description = "ARN of the test CodeBuild project"
  value       = var.create_test_project ? aws_codebuild_project.test_project[0].arn : null
}

# CodeDeploy
output "codedeploy_app_name" {
  description = "Name of the CodeDeploy application"
  value       = var.create_codedeploy_app ? aws_codedeploy_app.main[0].name : null
}

output "codedeploy_app_id" {
  description = "ID of the CodeDeploy application"
  value       = var.create_codedeploy_app ? aws_codedeploy_app.main[0].id : null
}

output "deployment_group_name" {
  description = "Name of the CodeDeploy deployment group"
  value       = var.create_codedeploy_app && var.create_deployment_group ? aws_codedeploy_deployment_group.main[0].deployment_group_name : null
}

output "deployment_group_id" {
  description = "ID of the CodeDeploy deployment group"
  value       = var.create_codedeploy_app && var.create_deployment_group ? aws_codedeploy_deployment_group.main[0].id : null
}

# CodePipeline
output "pipeline_name" {
  description = "Name of the CodePipeline"
  value       = var.create_pipeline ? aws_codepipeline.main[0].name : null
}

output "pipeline_arn" {
  description = "ARN of the CodePipeline"
  value       = var.create_pipeline ? aws_codepipeline.main[0].arn : null
}

# CloudWatch Alarms
output "pipeline_failures_alarm_name" {
  description = "Name of the pipeline failures CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.pipeline_failures[0].alarm_name : null
}

output "pipeline_failures_alarm_arn" {
  description = "ARN of the pipeline failures CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.pipeline_failures[0].arn : null
}

output "build_failures_alarm_name" {
  description = "Name of the build failures CloudWatch alarm"
  value       = var.create_alarms && var.create_build_project ? aws_cloudwatch_metric_alarm.build_failures[0].alarm_name : null
}

output "build_failures_alarm_arn" {
  description = "ARN of the build failures CloudWatch alarm"
  value       = var.create_alarms && var.create_build_project ? aws_cloudwatch_metric_alarm.build_failures[0].arn : null
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