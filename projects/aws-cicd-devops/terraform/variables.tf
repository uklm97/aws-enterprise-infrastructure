# AWS CI/CD & DevOps Platform - Variables
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
  default     = "aws-cicd-devops"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "production"
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Source Configuration
variable "source_provider" {
  description = "Source provider for CodePipeline (CodeCommit, GitHub, S3)"
  type        = string
  default     = "CodeCommit"
  validation {
    condition     = contains(["CodeCommit", "GitHub", "S3"], var.source_provider)
    error_message = "Source provider must be CodeCommit, GitHub, or S3."
  }
}

variable "source_repository" {
  description = "Name of the source repository (for CodeCommit)"
  type        = string
  default     = ""
}

variable "source_branch" {
  description = "Source branch name"
  type        = string
  default     = "main"
}

# GitHub Configuration
variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = ""
}

variable "github_token" {
  description = "GitHub OAuth token"
  type        = string
  default     = ""
  sensitive   = true
}

# Build Configuration
variable "create_build_project" {
  description = "Whether to create CodeBuild project"
  type        = bool
  default     = true
}

variable "build_compute_type" {
  description = "CodeBuild compute type"
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
  validation {
    condition = contains([
      "BUILD_GENERAL1_SMALL",
      "BUILD_GENERAL1_MEDIUM",
      "BUILD_GENERAL1_LARGE",
      "BUILD_GENERAL1_2XLARGE"
    ], var.build_compute_type)
    error_message = "Build compute type must be a valid CodeBuild compute type."
  }
}

variable "build_image" {
  description = "CodeBuild image"
  type        = string
  default     = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
}

variable "build_timeout" {
  description = "CodeBuild timeout in minutes"
  type        = number
  default     = 60
}

variable "build_privileged_mode" {
  description = "Whether to enable privileged mode for CodeBuild"
  type        = bool
  default     = false
}

variable "buildspec_file" {
  description = "Buildspec file name"
  type        = string
  default     = "buildspec.yml"
}

variable "build_environment_variables" {
  description = "Environment variables for CodeBuild"
  type        = map(string)
  default     = {}
}

# Test Configuration
variable "create_test_project" {
  description = "Whether to create test CodeBuild project"
  type        = bool
  default     = true
}

variable "test_compute_type" {
  description = "Test CodeBuild compute type"
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "test_image" {
  description = "Test CodeBuild image"
  type        = string
  default     = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
}

variable "test_timeout" {
  description = "Test CodeBuild timeout in minutes"
  type        = number
  default     = 30
}

variable "test_privileged_mode" {
  description = "Whether to enable privileged mode for test CodeBuild"
  type        = bool
  default     = false
}

variable "test_buildspec_file" {
  description = "Test buildspec file name"
  type        = string
  default     = "test-buildspec.yml"
}

variable "test_environment_variables" {
  description = "Environment variables for test CodeBuild"
  type        = map(string)
  default     = {}
}

# CodeDeploy Configuration
variable "create_codedeploy_app" {
  description = "Whether to create CodeDeploy application"
  type        = bool
  default     = true
}

variable "codedeploy_compute_platform" {
  description = "CodeDeploy compute platform"
  type        = string
  default     = "Server"
  validation {
    condition     = contains(["Server", "Lambda", "ECS"], var.codedeploy_compute_platform)
    error_message = "CodeDeploy compute platform must be Server, Lambda, or ECS."
  }
}

variable "create_deployment_group" {
  description = "Whether to create deployment group"
  type        = bool
  default     = true
}

variable "codedeploy_config_name" {
  description = "CodeDeploy deployment configuration name"
  type        = string
  default     = "CodeDeployDefault.OneAtATime"
}

variable "ec2_tag_filters" {
  description = "EC2 tag filters for deployment group"
  type = list(object({
    type  = string
    key   = string
    value = string
  }))
  default = [
    {
      type  = "KEY_AND_VALUE"
      key   = "Environment"
      value = "production"
    }
  ]
}

variable "auto_rollback_enabled" {
  description = "Whether to enable auto rollback"
  type        = bool
  default     = true
}

variable "auto_rollback_events" {
  description = "Events that trigger auto rollback"
  type        = list(string)
  default     = ["DEPLOYMENT_FAILURE"]
}

variable "alarm_configuration" {
  description = "CloudWatch alarm configuration for deployment"
  type = object({
    enabled                   = bool
    alarms                   = list(string)
    ignore_poll_alarm_failure = bool
  })
  default = null
}

# Pipeline Configuration
variable "create_pipeline" {
  description = "Whether to create CodePipeline"
  type        = bool
  default     = true
}

# Monitoring Configuration
variable "create_alarms" {
  description = "Whether to create CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alarm_sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  type        = string
  default     = null
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}