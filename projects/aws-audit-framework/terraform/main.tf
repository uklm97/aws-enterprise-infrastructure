terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Component   = "AuditFramework"
    }
  }
}

# Security Audit Module
module "security_audit" {
  source = "./modules/security_audit"
  
  project_name = var.project_name
  environment  = var.environment
  
  enable_iam_analysis      = var.enable_iam_analysis
  enable_security_groups   = var.enable_security_groups
  enable_vpc_audit         = var.enable_vpc_audit
  enable_encryption_audit  = var.enable_encryption_audit
}

# Cost Audit Module
module "cost_audit" {
  source = "./modules/cost_audit"
  
  project_name = var.project_name
  environment  = var.environment
  
  enable_cost_analysis     = var.enable_cost_analysis
  enable_budget_alerts     = var.enable_budget_alerts
  enable_utilization_audit = var.enable_utilization_audit
}

# Performance Audit Module
module "performance_audit" {
  source = "./modules/performance_audit"
  
  project_name = var.project_name
  environment  = var.environment
  
  enable_performance_monitoring = var.enable_performance_monitoring
  enable_cloudwatch_dashboards  = var.enable_cloudwatch_dashboards
  enable_alerts                 = var.enable_alerts
}

# Compliance Audit Module
module "compliance_audit" {
  source = "./modules/compliance_audit"
  
  project_name = var.project_name
  environment  = var.environment
  
  enable_config_rules     = var.enable_config_rules
  enable_cis_benchmarks   = var.enable_cis_benchmarks
  enable_compliance_alerts = var.enable_compliance_alerts
}

# S3 Bucket for Audit Logs
resource "aws_s3_bucket" "audit_logs" {
  bucket = "${var.project_name}-audit-logs-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-audit-logs"
    Environment = var.environment
    Purpose     = "Audit Logs Storage"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Policy
resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    id     = "audit_logs_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555  # 7 years
    }
  }
}

# CloudWatch Log Group for Audit Framework
resource "aws_cloudwatch_log_group" "audit_framework" {
  name              = "/aws/audit-framework/${var.project_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-audit-framework-logs"
    Environment = var.environment
  }
}

# SNS Topic for Audit Alerts
resource "aws_sns_topic" "audit_alerts" {
  name = "${var.project_name}-audit-alerts"

  tags = {
    Name        = "${var.project_name}-audit-alerts"
    Environment = var.environment
  }
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "audit_alerts_email" {
  count     = var.enable_email_alerts ? 1 : 0
  topic_arn = aws_sns_topic.audit_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_address
}

# IAM Role for Audit Framework
resource "aws_iam_role" "audit_framework_role" {
  name = "${var.project_name}-audit-framework-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-audit-framework-role"
    Environment = var.environment
  }
}

# IAM Policy for Audit Framework
resource "aws_iam_role_policy" "audit_framework_policy" {
  name = "${var.project_name}-audit-framework-policy"
  role = aws_iam_role.audit_framework_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:ListUsers",
          "iam:ListRoles",
          "iam:ListPolicies",
          "iam:GetUser",
          "iam:GetRole",
          "iam:GetPolicy",
          "iam:ListAccessKeys",
          "iam:ListMFADevices",
          "iam:GetAccountPasswordPolicy",
          "iam:GetAccountSummary",
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVpcs",
          "ec2:DescribeVolumes",
          "ec2:DescribeFlowLogs",
          "ec2:DescribeNetworkAcls",
          "s3:ListAllMyBuckets",
          "s3:GetBucketEncryption",
          "s3:GetBucketVersioning",
          "s3:GetBucketPublicAccessBlock",
          "rds:DescribeDBInstances",
          "kms:ListKeys",
          "kms:DescribeKey",
          "ce:GetCostAndUsage",
          "ce:GetReservationUtilization",
          "ce:GetReservationCoverage",
          "config:DescribeConfigRules",
          "config:GetComplianceDetailsByConfigRule",
          "config:DescribeConfigurationRecorders",
          "cloudwatch:GetMetricData",
          "cloudwatch:DescribeAlarms",
          "cloudtrail:DescribeTrails",
          "cloudtrail:GetTrailStatus",
          "guardduty:ListDetectors",
          "guardduty:ListFindings",
          "securityhub:GetFindings",
          "securityhub:ListFindings"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.audit_framework.arn}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.audit_logs.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.audit_alerts.arn
      }
    ]
  })
}

# Lambda Function for Audit Framework
resource "aws_lambda_function" "audit_framework" {
  filename         = "audit_framework.zip"
  function_name    = "${var.project_name}-audit-framework"
  role            = aws_iam_role.audit_framework_role.arn
  handler         = "audit_framework.lambda_handler"
  runtime         = "python3.9"
  timeout         = 900  # 15 minutes
  memory_size     = 512

  environment {
    variables = {
      PROJECT_NAME     = var.project_name
      ENVIRONMENT      = var.environment
      S3_BUCKET        = aws_s3_bucket.audit_logs.bucket
      SNS_TOPIC_ARN    = aws_sns_topic.audit_alerts.arn
      LOG_GROUP_NAME   = aws_cloudwatch_log_group.audit_framework.name
    }
  }

  tags = {
    Name        = "${var.project_name}-audit-framework"
    Environment = var.environment
  }
}

# EventBridge Rule for Scheduled Audits
resource "aws_cloudwatch_event_rule" "scheduled_audit" {
  name                = "${var.project_name}-scheduled-audit"
  description         = "Trigger audit framework on schedule"
  schedule_expression = var.audit_schedule

  tags = {
    Name        = "${var.project_name}-scheduled-audit"
    Environment = var.environment
  }
}

# EventBridge Target for Lambda
resource "aws_cloudwatch_event_target" "audit_framework_target" {
  rule      = aws_cloudwatch_event_rule.scheduled_audit.name
  target_id = "AuditFrameworkTarget"
  arn       = aws_lambda_function.audit_framework.arn
}

# Lambda Permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.audit_framework.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_audit.arn
}

# CloudWatch Dashboard for Audit Framework
resource "aws_cloudwatch_dashboard" "audit_framework" {
  dashboard_name = "${var.project_name}-audit-framework"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Config", "ConfigRuleComplianceChange", "RuleName", "iam-password-policy"],
            [".", "iam-user-mfa"],
            [".", "access-keys-rotated"],
            [".", "security-groups-restricted-common-ports"],
            [".", "vpc-default-security-group-closed"],
            [".", "vpc-flow-logs-enabled"],
            [".", "s3-bucket-encryption"],
            [".", "ebs-volume-encryption"],
            [".", "rds-encryption"]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Config Rule Compliance"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Config", "ConfigRuleComplianceChange", "RuleName", "iam-password-policy", { "stat": "Maximum" }],
            [".", "iam-user-mfa", { "stat": "Maximum" }],
            [".", "access-keys-rotated", { "stat": "Maximum" }],
            [".", "security-groups-restricted-common-ports", { "stat": "Maximum" }],
            [".", "vpc-default-security-group-closed", { "stat": "Maximum" }],
            [".", "vpc-flow-logs-enabled", { "stat": "Maximum" }],
            [".", "s3-bucket-encryption", { "stat": "Maximum" }],
            [".", "ebs-volume-encryption", { "stat": "Maximum" }],
            [".", "rds-encryption", { "stat": "Maximum" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Config Rule Compliance Rate"
        }
      }
    ]
  })
}

# CloudWatch Alarms for Audit Framework
resource "aws_cloudwatch_metric_alarm" "config_compliance_alarm" {
  alarm_name          = "${var.project_name}-config-compliance-alarm"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ConfigRuleComplianceChange"
  namespace           = "AWS/Config"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors Config rule compliance"
  alarm_actions       = [aws_sns_topic.audit_alerts.arn]

  dimensions = {
    RuleName = "iam-password-policy"
  }
}

# CloudWatch Alarms for Cost Monitoring
resource "aws_cloudwatch_metric_alarm" "cost_alarm" {
  alarm_name          = "${var.project_name}-cost-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # 24 hours
  statistic           = "Maximum"
  threshold           = var.cost_threshold
  alarm_description   = "This metric monitors AWS costs"
  alarm_actions       = [aws_sns_topic.audit_alerts.arn]

  dimensions = {
    Currency = "USD"
  }
}
