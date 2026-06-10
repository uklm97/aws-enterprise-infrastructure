terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "aws-cost-governance-terraform-state"
    key            = "cost-governance/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Component   = "CostGovernance"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# SNS topics for cost alerts
resource "aws_sns_topic" "cost_alerts" {
  count = var.create_sns_topics ? 1 : 0
  name  = "${var.project_name}-cost-alerts"

  tags = {
    Name        = "${var.project_name}-cost-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic" "budget_alerts" {
  count = var.create_sns_topics ? 1 : 0
  name  = "${var.project_name}-budget-alerts"

  tags = {
    Name        = "${var.project_name}-budget-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic" "optimization_reports" {
  count = var.create_sns_topics ? 1 : 0
  name  = "${var.project_name}-optimization-reports"

  tags = {
    Name        = "${var.project_name}-optimization-reports"
    Environment = var.environment
  }
}

# SNS subscriptions
resource "aws_sns_topic_subscription" "cost_alerts_email" {
  count     = var.create_sns_topics && var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.cost_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_sns_topic_subscription" "budget_alerts_email" {
  count     = var.create_sns_topics && var.budget_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.budget_alerts[0].arn
  protocol  = "email"
  endpoint  = var.budget_email
}

resource "aws_sns_topic_subscription" "optimization_reports_email" {
  count     = var.create_sns_topics && var.report_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.optimization_reports[0].arn
  protocol  = "email"
  endpoint  = var.report_email
}

# Budgets
resource "aws_budgets_budget" "monthly_budget" {
  count = var.create_budgets ? 1 : 0
  name  = "${var.project_name}-monthly-budget"

  budget_type  = "COST"
  limit_amount = var.monthly_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Tag = var.budget_tags
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.budget_alerts[0].arn] : []
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.budget_alerts[0].arn] : []
  }

  tags = {
    Name        = "${var.project_name}-monthly-budget"
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "daily_budget" {
  count = var.create_budgets ? 1 : 0
  name  = "${var.project_name}-daily-budget"

  budget_type  = "COST"
  limit_amount = var.daily_budget_limit
  limit_unit   = "USD"
  time_unit    = "DAILY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 90
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []
  }

  tags = {
    Name        = "${var.project_name}-daily-budget"
    Environment = var.environment
  }
}

# Service-specific budgets
resource "aws_budgets_budget" "ec2_budget" {
  count = var.create_service_budgets ? 1 : 0
  name  = "${var.project_name}-ec2-budget"

  budget_type  = "COST"
  limit_amount = var.ec2_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon Elastic Compute Cloud - Compute"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []
  }

  tags = {
    Name        = "${var.project_name}-ec2-budget"
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "rds_budget" {
  count = var.create_service_budgets ? 1 : 0
  name  = "${var.project_name}-rds-budget"

  budget_type  = "COST"
  limit_amount = var.rds_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon Relational Database Service"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []
  }

  tags = {
    Name        = "${var.project_name}-rds-budget"
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "s3_budget" {
  count = var.create_service_budgets ? 1 : 0
  name  = "${var.project_name}-s3-budget"

  budget_type  = "COST"
  limit_amount = var.s3_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon Simple Storage Service"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = var.alert_email != "" ? [var.alert_email] : []
    subscriber_sns_topic_arns = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []
  }

  tags = {
    Name        = "${var.project_name}-s3-budget"
    Environment = var.environment
  }
}

# CloudWatch alarms for cost monitoring
resource "aws_cloudwatch_metric_alarm" "daily_cost_alarm" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-daily-cost-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # 24 hours
  statistic           = "Maximum"
  threshold           = var.daily_cost_threshold
  alarm_description   = "This metric monitors daily estimated charges"
  alarm_actions       = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []

  dimensions = {
    Currency = "USD"
  }

  tags = {
    Name        = "${var.project_name}-daily-cost-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "monthly_cost_alarm" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-monthly-cost-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "2592000"  # 30 days
  statistic           = "Maximum"
  threshold           = var.monthly_cost_threshold
  alarm_description   = "This metric monitors monthly estimated charges"
  alarm_actions       = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []

  dimensions = {
    Currency = "USD"
  }

  tags = {
    Name        = "${var.project_name}-monthly-cost-alarm"
    Environment = var.environment
  }
}

# Service-specific cost alarms
resource "aws_cloudwatch_metric_alarm" "ec2_cost_alarm" {
  count               = var.create_service_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-ec2-cost-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"
  statistic           = "Maximum"
  threshold           = var.ec2_cost_threshold
  alarm_description   = "This metric monitors EC2 estimated charges"
  alarm_actions       = var.create_sns_topics ? [aws_sns_topic.cost_alerts[0].arn] : []

  dimensions = {
    ServiceName = "Amazon Elastic Compute Cloud - Compute"
    Currency    = "USD"
  }

  tags = {
    Name        = "${var.project_name}-ec2-cost-alarm"
    Environment = var.environment
  }
}

# Cost allocation tags
resource "aws_ce_cost_category" "cost_allocation" {
  count = var.create_cost_allocation_tags ? 1 : 0
  name  = "${var.project_name}-cost-allocation"

  rule {
    value = "Environment"
    rule {
      dimension {
        key   = "TAG"
        values = ["Environment"]
      }
    }
  }

  rule {
    value = "Project"
    rule {
      dimension {
        key   = "TAG"
        values = ["Project"]
      }
    }
  }

  rule {
    value = "Component"
    rule {
      dimension {
        key   = "TAG"
        values = ["Component"]
      }
    }
  }

  rule {
    value = "CostCenter"
    rule {
      dimension {
        key   = "TAG"
        values = ["CostCenter"]
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-cost-allocation"
    Environment = var.environment
  }
}

# Cost anomaly detection
resource "aws_ce_anomaly_detector" "cost_anomaly" {
  count = var.create_anomaly_detection ? 1 : 0
  name  = "${var.project_name}-cost-anomaly-detector"

  specification = "DAILY_COST"

  tags = {
    Name        = "${var.project_name}-cost-anomaly-detector"
    Environment = var.environment
  }
}

# CloudWatch dashboards
resource "aws_cloudwatch_dashboard" "cost_dashboard" {
  count = var.create_dashboards ? 1 : 0
  dashboard_name = "${var.project_name}-cost-dashboard"

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
            ["AWS/Billing", "EstimatedCharges", "Currency", "USD"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Daily Estimated Charges"
          period  = 86400
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "Amazon Elastic Compute Cloud - Compute", "Currency", "USD"],
            [".", ".", ".", "Amazon Simple Storage Service", ".", "."],
            [".", ".", ".", "Amazon Relational Database Service", ".", "."],
            [".", ".", ".", "AWS Lambda", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Cost by Service"
          period  = 86400
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-cost-dashboard"
    Environment = var.environment
  }
}

# Lambda function for cost automation
resource "aws_lambda_function" "cost_automation" {
  count = var.create_lambda_functions ? 1 : 0
  filename         = "cost_automation.zip"
  function_name    = "${var.project_name}-cost-automation"
  role            = aws_iam_role.cost_automation_role[0].arn
  handler         = "cost_automation.handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      SNS_TOPIC_ARN = var.create_sns_topics ? aws_sns_topic.cost_alerts[0].arn : ""
      BUDGET_TOPIC_ARN = var.create_sns_topics ? aws_sns_topic.budget_alerts[0].arn : ""
      REPORT_TOPIC_ARN = var.create_sns_topics ? aws_sns_topic.optimization_reports[0].arn : ""
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.cost_automation_policy,
    aws_cloudwatch_log_group.cost_automation_logs
  ]

  tags = {
    Name        = "${var.project_name}-cost-automation"
    Environment = var.environment
  }
}

# IAM role for cost automation Lambda
resource "aws_iam_role" "cost_automation_role" {
  count = var.create_lambda_functions ? 1 : 0
  name = "${var.project_name}-cost-automation-role"

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
    Name        = "${var.project_name}-cost-automation-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "cost_automation_policy" {
  count      = var.create_lambda_functions ? 1 : 0
  role       = aws_iam_role.cost_automation_role[0].name
  policy_arn = aws_iam_policy.cost_automation_policy[0].arn
}

resource "aws_iam_policy" "cost_automation_policy" {
  count = var.create_lambda_functions ? 1 : 0
  name  = "${var.project_name}-cost-automation-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ce:*",
          "budgets:*",
          "sns:Publish",
          "cloudwatch:*",
          "ec2:Describe*",
          "rds:Describe*",
          "lambda:ListFunctions",
          "organizations:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-cost-automation-policy"
    Environment = var.environment
  }
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "cost_automation_logs" {
  count             = var.create_lambda_functions ? 1 : 0
  name              = "/aws/lambda/${var.project_name}-cost-automation"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-cost-automation-logs"
    Environment = var.environment
  }
}

# EventBridge rules for cost automation
resource "aws_cloudwatch_event_rule" "daily_cost_check" {
  count = var.create_eventbridge_rules ? 1 : 0
  name  = "${var.project_name}-daily-cost-check"

  description = "Daily cost threshold check"
  schedule_expression = "cron(0 9 * * ? *)"  # 9 AM UTC daily

  tags = {
    Name        = "${var.project_name}-daily-cost-check"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "daily_cost_check_lambda" {
  count     = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  rule      = aws_cloudwatch_event_rule.daily_cost_check[0].name
  target_id = "CostAutomationTarget"
  arn       = aws_lambda_function.cost_automation[0].arn
}

resource "aws_lambda_permission" "allow_eventbridge_daily" {
  count         = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_automation[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_cost_check[0].arn
}

resource "aws_cloudwatch_event_rule" "weekly_optimization" {
  count = var.create_eventbridge_rules ? 1 : 0
  name  = "${var.project_name}-weekly-optimization"

  description = "Weekly cost optimization"
  schedule_expression = "cron(0 10 ? * MON *)"  # 10 AM UTC every Monday

  tags = {
    Name        = "${var.project_name}-weekly-optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "weekly_optimization_lambda" {
  count     = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  rule      = aws_cloudwatch_event_rule.weekly_optimization[0].name
  target_id = "WeeklyOptimizationTarget"
  arn       = aws_lambda_function.cost_automation[0].arn
}

resource "aws_lambda_permission" "allow_eventbridge_weekly" {
  count         = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridgeWeekly"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_automation[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_optimization[0].arn
}

# S3 bucket for cost reports
resource "aws_s3_bucket" "cost_reports" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = "${var.project_name}-cost-reports-${random_string.bucket_suffix[0].result}"

  tags = {
    Name        = "${var.project_name}-cost-reports"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "cost_reports" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.cost_reports[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cost_reports" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.cost_reports[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cost_reports" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.cost_reports[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Random string for S3 bucket suffix
resource "random_string" "bucket_suffix" {
  count   = var.create_s3_bucket ? 1 : 0
  length  = 8
  special = false
  upper   = false
}

# Cost and usage report
resource "aws_cur_report_definition" "cost_usage_report" {
  count = var.create_cost_usage_report ? 1 : 0

  report_name                = "${var.project_name}-cost-usage-report"
  time_unit                  = "DAILY"
  format                     = "textORcsv"
  compression                = "GZIP"
  additional_schema_elements = ["RESOURCES"]
  s3_bucket                  = aws_s3_bucket.cost_reports[0].bucket
  s3_prefix                  = "cost-usage-reports/"
  s3_region                  = var.aws_region
  additional_artifacts       = ["REDSHIFT", "QUICKSIGHT"]
  refresh_cadence            = "CreateOnce"

  depends_on = [aws_s3_bucket_policy.cost_reports_policy]
}

# S3 bucket policy for Cost and Usage Reports
resource "aws_s3_bucket_policy" "cost_reports_policy" {
  count  = var.create_cost_usage_report ? 1 : 0
  bucket = aws_s3_bucket.cost_reports[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSBillingReportPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::386209384616:root"  # AWS Billing account
        }
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy"
        ]
        Resource = aws_s3_bucket.cost_reports[0].arn
      },
      {
        Sid    = "AWSBillingReportPermissions2"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::386209384616:root"
        }
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.cost_reports[0].arn}/*"
      }
    ]
  })
}