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
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Automation  = "aws-operations"
    }
  }
}

# S3 Bucket for automation logs and artifacts
resource "aws_s3_bucket" "automation_logs" {
  bucket = "${var.project_name}-automation-logs-${random_string.bucket_suffix.result}"
  
  tags = {
    Name        = "${var.project_name}-automation-logs"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "automation_logs" {
  bucket = aws_s3_bucket.automation_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "automation_logs" {
  bucket = aws_s3_bucket.automation_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "automation_logs" {
  bucket = aws_s3_bucket.automation_logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    expiration {
      days = var.log_retention_days
    }
  }
}

# Random string for bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# CloudWatch Log Group for Lambda functions
resource "aws_cloudwatch_log_group" "automation_lambda" {
  name              = "/aws/lambda/${var.project_name}-automation"
  retention_in_days = var.log_retention_days
  
  tags = {
    Name        = "${var.project_name}-automation-logs"
    Environment = var.environment
  }
}

# SNS Topic for notifications
resource "aws_sns_topic" "automation_alerts" {
  name = "${var.project_name}-automation-alerts"
  
  tags = {
    Name        = "${var.project_name}-automation-alerts"
    Environment = var.environment
  }
}

# IAM Role for Lambda functions
resource "aws_iam_role" "automation_lambda_role" {
  name = "${var.project_name}-automation-lambda-role"

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
    Name        = "${var.project_name}-automation-lambda-role"
    Environment = var.environment
  }
}

# IAM Policy for Lambda functions
resource "aws_iam_role_policy" "automation_lambda_policy" {
  name = "${var.project_name}-automation-lambda-policy"
  role = aws_iam_role.automation_lambda_role.id

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
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:CreateSnapshot",
          "ec2:DeleteSnapshot",
          "ec2:CopySnapshot",
          "ec2:DescribeImages",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeLoadBalancers",
          "ec2:DescribeAutoScalingGroups"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.automation_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.automation_logs.arn,
          "${aws_s3_bucket.automation_logs.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:ListUsers",
          "iam:ListRoles",
          "iam:ListPolicies",
          "iam:GetUser",
          "iam:GetRole",
          "iam:GetPolicy"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBSnapshots",
          "rds:CreateDBSnapshot",
          "rds:DeleteDBSnapshot"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda function for instance scheduling
resource "aws_lambda_function" "instance_scheduler" {
  filename         = "lambda_functions/instance_scheduler.zip"
  function_name    = "${var.project_name}-instance-scheduler"
  role            = aws_iam_role.automation_lambda_role.arn
  handler         = "scheduled_start_stop.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      AWS_REGION = var.aws_region
      SNS_TOPIC_ARN = aws_sns_topic.automation_alerts.arn
      LOG_GROUP_NAME = aws_cloudwatch_log_group.automation_lambda.name
    }
  }

  depends_on = [
    aws_iam_role_policy.automation_lambda_policy,
    aws_cloudwatch_log_group.automation_lambda
  ]

  tags = {
    Name        = "${var.project_name}-instance-scheduler"
    Environment = var.environment
  }
}

# Lambda function for snapshot management
resource "aws_lambda_function" "snapshot_manager" {
  filename         = "lambda_functions/snapshot_manager.zip"
  function_name    = "${var.project_name}-snapshot-manager"
  role            = aws_iam_role.automation_lambda_role.arn
  handler         = "snapshot_manager.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      AWS_REGION = var.aws_region
      SNS_TOPIC_ARN = aws_sns_topic.automation_alerts.arn
      LOG_GROUP_NAME = aws_cloudwatch_log_group.automation_lambda.name
    }
  }

  depends_on = [
    aws_iam_role_policy.automation_lambda_policy,
    aws_cloudwatch_log_group.automation_lambda
  ]

  tags = {
    Name        = "${var.project_name}-snapshot-manager"
    Environment = var.environment
  }
}

# EventBridge rules for scheduling

# Daily instance start (8 AM)
resource "aws_cloudwatch_event_rule" "daily_instance_start" {
  name                = "${var.project_name}-daily-instance-start"
  description         = "Start instances daily at 8 AM"
  schedule_expression = "cron(0 8 * * ? *)"

  tags = {
    Name        = "${var.project_name}-daily-instance-start"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "daily_instance_start_target" {
  rule      = aws_cloudwatch_event_rule.daily_instance_start.name
  target_id = "InstanceSchedulerStart"
  arn       = aws_lambda_function.instance_scheduler.arn

  input = jsonencode({
    action = "start"
  })
}

# Daily instance stop (6 PM)
resource "aws_cloudwatch_event_rule" "daily_instance_stop" {
  name                = "${var.project_name}-daily-instance-stop"
  description         = "Stop instances daily at 6 PM"
  schedule_expression = "cron(0 18 * * ? *)"

  tags = {
    Name        = "${var.project_name}-daily-instance-stop"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "daily_instance_stop_target" {
  rule      = aws_cloudwatch_event_rule.daily_instance_stop.name
  target_id = "InstanceSchedulerStop"
  arn       = aws_lambda_function.instance_scheduler.arn

  input = jsonencode({
    action = "stop"
  })
}

# Daily backup (2 AM)
resource "aws_cloudwatch_event_rule" "daily_backup" {
  name                = "${var.project_name}-daily-backup"
  description         = "Create daily snapshots at 2 AM"
  schedule_expression = "cron(0 2 * * ? *)"

  tags = {
    Name        = "${var.project_name}-daily-backup"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "daily_backup_target" {
  rule      = aws_cloudwatch_event_rule.daily_backup.name
  target_id = "SnapshotManagerDaily"
  arn       = aws_lambda_function.snapshot_manager.arn

  input = jsonencode({
    action = "daily_backup"
  })
}

# Weekly backup (Sunday 3 AM)
resource "aws_cloudwatch_event_rule" "weekly_backup" {
  name                = "${var.project_name}-weekly-backup"
  description         = "Create weekly snapshots on Sunday at 3 AM"
  schedule_expression = "cron(0 3 ? * SUN *)"

  tags = {
    Name        = "${var.project_name}-weekly-backup"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "weekly_backup_target" {
  rule      = aws_cloudwatch_event_rule.weekly_backup.name
  target_id = "SnapshotManagerWeekly"
  arn       = aws_lambda_function.snapshot_manager.arn

  input = jsonencode({
    action = "weekly_backup"
  })
}

# Monthly backup (1st of month 4 AM)
resource "aws_cloudwatch_event_rule" "monthly_backup" {
  name                = "${var.project_name}-monthly-backup"
  description         = "Create monthly snapshots on 1st of month at 4 AM"
  schedule_expression = "cron(0 4 1 * ? *)"

  tags = {
    Name        = "${var.project_name}-monthly-backup"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "monthly_backup_target" {
  rule      = aws_cloudwatch_event_rule.monthly_backup.name
  target_id = "SnapshotManagerMonthly"
  arn       = aws_lambda_function.snapshot_manager.arn

  input = jsonencode({
    action = "monthly_backup"
  })
}

# Lambda permissions for EventBridge
resource "aws_lambda_permission" "allow_eventbridge_instance_scheduler" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.instance_scheduler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_instance_start.arn
}

resource "aws_lambda_permission" "allow_eventbridge_snapshot_manager" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.snapshot_manager.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_backup.arn
}

# CloudWatch Dashboard for monitoring
resource "aws_cloudwatch_dashboard" "automation_dashboard" {
  dashboard_name = "${var.project_name}-automation-dashboard"

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
            ["AWS/OperationsAutomation", "InstancesStarted", "ProjectName", var.project_name],
            [".", "InstancesStopped", ".", "."],
            [".", "EstimatedSavings", ".", "."]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Instance Automation Metrics"
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
            ["AWS/OperationsAutomation", "SnapshotsCreated", "ProjectName", var.project_name],
            [".", "SnapshotsDeleted", ".", "."],
            [".", "CrossRegionCopies", ".", "."],
            [".", "TotalBackupSize", ".", "."]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Backup Automation Metrics"
        }
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "automation_failure_alarm" {
  alarm_name          = "${var.project_name}-automation-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors automation lambda function errors"
  alarm_actions       = [aws_sns_topic.automation_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.instance_scheduler.function_name
  }

  tags = {
    Name        = "${var.project_name}-automation-failure"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "backup_failure_alarm" {
  alarm_name          = "${var.project_name}-backup-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors backup lambda function errors"
  alarm_actions       = [aws_sns_topic.automation_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.snapshot_manager.function_name
  }

  tags = {
    Name        = "${var.project_name}-backup-failure"
    Environment = var.environment
  }
}

# SNS Topic Subscription (email)
resource "aws_sns_topic_subscription" "automation_alerts_email" {
  count     = var.enable_email_notifications ? 1 : 0
  topic_arn = aws_sns_topic.automation_alerts.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# Outputs
output "automation_logs_bucket" {
  description = "S3 bucket for automation logs"
  value       = aws_s3_bucket.automation_logs.bucket
}

output "automation_alerts_topic" {
  description = "SNS topic for automation alerts"
  value       = aws_sns_topic.automation_alerts.arn
}

output "instance_scheduler_function" {
  description = "Lambda function for instance scheduling"
  value       = aws_lambda_function.instance_scheduler.function_name
}

output "snapshot_manager_function" {
  description = "Lambda function for snapshot management"
  value       = aws_lambda_function.snapshot_manager.function_name
}

output "automation_dashboard" {
  description = "CloudWatch dashboard for monitoring"
  value       = aws_cloudwatch_dashboard.automation_dashboard.dashboard_name
}
