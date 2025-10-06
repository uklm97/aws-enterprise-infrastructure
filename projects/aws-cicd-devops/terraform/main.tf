# AWS CI/CD & DevOps Platform - Main Terraform Configuration
# This file creates the core infrastructure for the CI/CD platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random string for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket for CodePipeline artifacts
resource "aws_s3_bucket" "pipeline_artifacts" {
  bucket = "${var.project_name}-pipeline-artifacts-${random_string.suffix.result}"
  
  tags = {
    Name        = "${var.project_name}-pipeline-artifacts"
    Environment = var.environment
    Purpose     = "codepipeline-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id

  rule {
    id     = "delete_old_artifacts"
    status = "Enabled"

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# S3 Bucket for CodeBuild cache
resource "aws_s3_bucket" "build_cache" {
  bucket = "${var.project_name}-build-cache-${random_string.suffix.result}"
  
  tags = {
    Name        = "${var.project_name}-build-cache"
    Environment = var.environment
    Purpose     = "codebuild-cache"
  }
}

resource "aws_s3_bucket_versioning" "build_cache" {
  bucket = aws_s3_bucket.build_cache.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "pipeline_logs" {
  name              = "/aws/codepipeline/${var.project_name}"
  retention_in_days = var.log_retention_days
  
  tags = {
    Name        = "${var.project_name}-pipeline-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "build_logs" {
  name              = "/aws/codebuild/${var.project_name}"
  retention_in_days = var.log_retention_days
  
  tags = {
    Name        = "${var.project_name}-build-logs"
    Environment = var.environment
  }
}

# IAM Roles
resource "aws_iam_role" "codepipeline_role" {
  name = "${var.project_name}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-codepipeline-role"
    Environment = var.environment
  }
}

resource "aws_iam_role" "codebuild_role" {
  name = "${var.project_name}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-codebuild-role"
    Environment = var.environment
  }
}

resource "aws_iam_role" "codedeploy_role" {
  name = "${var.project_name}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-codedeploy-role"
    Environment = var.environment
  }
}

# IAM Policies
resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "${var.project_name}-codepipeline-policy"
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:GetBucketVersioning",
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.pipeline_artifacts.arn,
          "${aws_s3_bucket.pipeline_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codecommit:CancelUploadArchive",
          "codecommit:GetBranch",
          "codecommit:GetCommit",
          "codecommit:GetRepository",
          "codecommit:GetUploadArchiveStatus",
          "codecommit:UploadArchive"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:BatchGetProjects",
          "codebuild:StartBuild",
          "codebuild:StopBuild"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "codedeploy:CreateDeployment",
          "codedeploy:GetApplication",
          "codedeploy:GetApplicationRevision",
          "codedeploy:GetDeployment",
          "codedeploy:GetDeploymentConfig",
          "codedeploy:RegisterApplicationRevision"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.codebuild_role.arn,
          aws_iam_role.codedeploy_role.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "codebuild_policy" {
  name = "${var.project_name}-codebuild-policy"
  role = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_cloudwatch_log_group.build_logs.arn,
          "${aws_cloudwatch_log_group.build_logs.arn}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.pipeline_artifacts.arn,
          "${aws_s3_bucket.pipeline_artifacts.arn}/*",
          aws_s3_bucket.build_cache.arn,
          "${aws_s3_bucket.build_cache.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "codedeploy_policy" {
  name = "${var.project_name}-codedeploy-policy"
  role = aws_iam_role.codedeploy_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateTags",
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:DescribeTags"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "autoscaling:CompleteLifecycleAction",
          "autoscaling:DeleteLifecycleHook",
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:DescribeLifecycleHooks",
          "autoscaling:PutLifecycleHook",
          "autoscaling:RecordLifecycleActionHeartbeat"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetHealth",
          "elasticloadbalancing:ModifyListener",
          "elasticloadbalancing:ModifyTargetGroup",
          "elasticloadbalancing:SetIpAddressType"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = [
          aws_s3_bucket.pipeline_artifacts.arn,
          "${aws_s3_bucket.pipeline_artifacts.arn}/*"
        ]
      }
    ]
  })
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "codepipeline_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/AWSCodePipelineServiceRole"
  role       = aws_iam_role.codepipeline_role.name
}

resource "aws_iam_role_policy_attachment" "codebuild_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
  role       = aws_iam_role.codebuild_role.name
}

resource "aws_iam_role_policy_attachment" "codedeploy_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRole"
  role       = aws_iam_role.codedeploy_role.name
}

# CodeBuild Projects
resource "aws_codebuild_project" "build_project" {
  count = var.create_build_project ? 1 : 0
  
  name          = "${var.project_name}-build"
  description   = "Build project for ${var.project_name}"
  service_role  = aws_iam_role.codebuild_role.arn
  build_timeout = var.build_timeout

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = var.build_compute_type
    image                       = var.build_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = var.build_privileged_mode

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    dynamic "environment_variable" {
      for_each = var.build_environment_variables
      content {
        name  = environment_variable.key
        value = environment_variable.value
      }
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = var.buildspec_file
  }

  cache {
    type  = "S3"
    location = aws_s3_bucket.build_cache.bucket
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.build_logs.name
      stream_name = "build"
    }
  }

  tags = {
    Name        = "${var.project_name}-build"
    Environment = var.environment
  }
}

resource "aws_codebuild_project" "test_project" {
  count = var.create_test_project ? 1 : 0
  
  name          = "${var.project_name}-test"
  description   = "Test project for ${var.project_name}"
  service_role  = aws_iam_role.codebuild_role.arn
  build_timeout = var.test_timeout

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = var.test_compute_type
    image                       = var.test_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = var.test_privileged_mode

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }

    dynamic "environment_variable" {
      for_each = var.test_environment_variables
      content {
        name  = environment_variable.key
        value = environment_variable.value
      }
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = var.test_buildspec_file
  }

  cache {
    type  = "S3"
    location = aws_s3_bucket.build_cache.bucket
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.build_logs.name
      stream_name = "test"
    }
  }

  tags = {
    Name        = "${var.project_name}-test"
    Environment = var.environment
  }
}

# CodeDeploy Application
resource "aws_codedeploy_app" "main" {
  count = var.create_codedeploy_app ? 1 : 0
  
  compute_platform = var.codedeploy_compute_platform
  name             = var.project_name

  tags = {
    Name        = var.project_name
    Environment = var.environment
  }
}

# CodeDeploy Deployment Group
resource "aws_codedeploy_deployment_group" "main" {
  count = var.create_codedeploy_app && var.create_deployment_group ? 1 : 0
  
  app_name              = aws_codedeploy_app.main[0].name
  deployment_group_name = "${var.project_name}-deployment-group"
  service_role_arn      = aws_iam_role.codedeploy_role.arn

  deployment_config_name = var.codedeploy_config_name

  dynamic "ec2_tag_filter" {
    for_each = var.ec2_tag_filters
    content {
      type  = ec2_tag_filter.value.type
      key   = ec2_tag_filter.value.key
      value = ec2_tag_filter.value.value
    }
  }

  dynamic "auto_rollback_configuration" {
    for_each = var.auto_rollback_enabled ? [1] : []
    content {
      enabled = true
      events  = var.auto_rollback_events
    }
  }

  dynamic "alarm_configuration" {
    for_each = var.alarm_configuration != null ? [var.alarm_configuration] : []
    content {
      enabled                   = alarm_configuration.value.enabled
      alarms                   = alarm_configuration.value.alarms
      ignore_poll_alarm_failure = alarm_configuration.value.ignore_poll_alarm_failure
    }
  }

  tags = {
    Name        = "${var.project_name}-deployment-group"
    Environment = var.environment
  }
}

# CodePipeline
resource "aws_codepipeline" "main" {
  count = var.create_pipeline ? 1 : 0
  
  name     = var.project_name
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.pipeline_artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = var.source_provider
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = var.source_provider == "CodeCommit" ? {
        RepositoryName = var.source_repository
        BranchName     = var.source_branch
      } : var.source_provider == "GitHub" ? {
        Owner  = var.github_owner
        Repo   = var.github_repo
        Branch = var.source_branch
        OAuthToken = var.github_token
      } : {}
    }
  }

  dynamic "stage" {
    for_each = var.create_build_project ? [1] : []
    content {
      name = "Build"

      action {
        name             = "Build"
        category         = "Build"
        owner            = "AWS"
        provider         = "CodeBuild"
        input_artifacts  = ["source_output"]
        output_artifacts = ["build_output"]
        version          = "1"

        configuration = {
          ProjectName = aws_codebuild_project.build_project[0].name
        }
      }
    }
  }

  dynamic "stage" {
    for_each = var.create_test_project ? [1] : []
    content {
      name = "Test"

      action {
        name             = "Test"
        category         = "Test"
        owner            = "AWS"
        provider         = "CodeBuild"
        input_artifacts  = ["build_output"]
        output_artifacts = ["test_output"]
        version          = "1"

        configuration = {
          ProjectName = aws_codebuild_project.test_project[0].name
        }
      }
    }
  }

  dynamic "stage" {
    for_each = var.create_codedeploy_app ? [1] : []
    content {
      name = "Deploy"

      action {
        name            = "Deploy"
        category        = "Deploy"
        owner           = "AWS"
        provider        = "CodeDeploy"
        input_artifacts = ["build_output"]
        version         = "1"

        configuration = {
          ApplicationName     = aws_codedeploy_app.main[0].name
          DeploymentGroupName = aws_codedeploy_deployment_group.main[0].deployment_group_name
        }
      }
    }
  }

  tags = {
    Name        = var.project_name
    Environment = var.environment
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "pipeline_failures" {
  count = var.create_alarms ? 1 : 0
  
  alarm_name          = "${var.project_name}-pipeline-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FailedExecutions"
  namespace           = "AWS/CodePipeline"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors pipeline failures"
  alarm_actions       = var.alarm_sns_topic_arn != null ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    PipelineName = var.project_name
  }

  tags = {
    Name        = "${var.project_name}-pipeline-failures"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "build_failures" {
  count = var.create_alarms && var.create_build_project ? 1 : 0
  
  alarm_name          = "${var.project_name}-build-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FailedBuilds"
  namespace           = "AWS/CodeBuild"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors build failures"
  alarm_actions       = var.alarm_sns_topic_arn != null ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    ProjectName = aws_codebuild_project.build_project[0].name
  }

  tags = {
    Name        = "${var.project_name}-build-failures"
    Environment = var.environment
  }
}