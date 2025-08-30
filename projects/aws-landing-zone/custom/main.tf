terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "aws-landing-zone-terraform-state"
    key            = "landing-zone/terraform.tfstate"
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
      Component   = "LandingZone"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# AWS Organizations
resource "aws_organizations_organization" "main" {
  feature_set = "ALL"
  
  aws_service_access_principals = [
    "cloudtrail.amazonaws.com",
    "config.amazonaws.com",
    "sso.amazonaws.com",
    "securityhub.amazonaws.com",
    "guardduty.amazonaws.com",
    "macie.amazonaws.com",
    "config-multiaccountsetup.amazonaws.com"
  ]
  
  enabled_policy_types = [
    "SERVICE_CONTROL_POLICY",
    "TAG_POLICY"
  ]
}

# Organizational Units
resource "aws_organizations_organizational_unit" "security" {
  name      = "Security"
  parent_id = aws_organizations_organization.main.roots[0].id
  
  tags = {
    Name        = "Security OU"
    Description = "Security and compliance accounts"
  }
}

resource "aws_organizations_organizational_unit" "infrastructure" {
  name      = "Infrastructure"
  parent_id = aws_organizations_organization.main.roots[0].id
  
  tags = {
    Name        = "Infrastructure OU"
    Description = "Shared services and networking accounts"
  }
}

resource "aws_organizations_organizational_unit" "workloads" {
  name      = "Workloads"
  parent_id = aws_organizations_organization.main.roots[0].id
  
  tags = {
    Name        = "Workloads OU"
    Description = "Application and workload accounts"
  }
}

resource "aws_organizations_organizational_unit" "sandbox" {
  name      = "Sandbox"
  parent_id = aws_organizations_organization.main.roots[0].id
  
  tags = {
    Name        = "Sandbox OU"
    Description = "Development and testing accounts"
  }
}

# AWS SSO
resource "aws_ssoadmin_instance" "main" {
  name = "${var.project_name}-sso"
  
  tags = {
    Name = "${var.project_name}-sso-instance"
  }
}

# AWS SSO Permission Sets
resource "aws_ssoadmin_permission_set" "administrator" {
  name             = "Administrator"
  description      = "Full administrator access"
  instance_arn     = aws_ssoadmin_instance.main.arn
  session_duration = "PT8H"
  
  tags = {
    Name = "Administrator-PermissionSet"
  }
}

resource "aws_ssoadmin_permission_set" "developer" {
  name             = "Developer"
  description      = "Developer access with limited permissions"
  instance_arn     = aws_ssoadmin_instance.main.arn
  session_duration = "PT8H"
  
  tags = {
    Name = "Developer-PermissionSet"
  }
}

resource "aws_ssoadmin_permission_set" "readonly" {
  name             = "ReadOnly"
  description      = "Read-only access"
  instance_arn     = aws_ssoadmin_instance.main.arn
  session_duration = "PT8H"
  
  tags = {
    Name = "ReadOnly-PermissionSet"
  }
}

# Attach managed policies to permission sets
resource "aws_ssoadmin_managed_policy_attachment" "administrator" {
  instance_arn       = aws_ssoadmin_instance.main.arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_ssoadmin_managed_policy_attachment" "developer" {
  instance_arn       = aws_ssoadmin_instance.main.arn
  permission_set_arn = aws_ssoadmin_permission_set.developer.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

resource "aws_ssoadmin_managed_policy_attachment" "readonly" {
  instance_arn       = aws_ssoadmin_instance.main.arn
  permission_set_arn = aws_ssoadmin_permission_set.readonly.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# AWS Config
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.project_name}-config-recorder"
  role_arn = aws_iam_role.config_role.arn
  
  recording_group {
    all_supported = true
    include_global_resources = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.project_name}-config-delivery"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
  s3_key_prefix  = "config"
  
  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  recording  = true
  
  depends_on = [aws_config_delivery_channel.main]
}

# CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "${var.project_name}-cloudtrail"
  s3_bucket_name               = aws_s3_bucket.cloudtrail_bucket.bucket
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  
  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::"]
    }
  }
  
  tags = {
    Name = "${var.project_name}-cloudtrail"
  }
}

# S3 Buckets for logging
resource "aws_s3_bucket" "config_bucket" {
  bucket = "${var.project_name}-config-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name = "${var.project_name}-config-bucket"
  }
}

resource "aws_s3_bucket" "cloudtrail_bucket" {
  bucket = "${var.project_name}-cloudtrail-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name = "${var.project_name}-cloudtrail-bucket"
  }
}

# S3 bucket configurations
resource "aws_s3_bucket_versioning" "config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "cloudtrail_bucket" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_bucket" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_bucket" {
  bucket = aws_s3_bucket.cloudtrail_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Roles
resource "aws_iam_role" "config_role" {
  name = "${var.project_name}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "config_role" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "config" {
  name              = "/aws/config/${var.project_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-config-logs"
  }
}

resource "aws_cloudwatch_log_group" "cloudtrail" {
  name              = "/aws/cloudtrail/${var.project_name}"
  retention_in_days = 30
  
  tags = {
    Name = "${var.project_name}-cloudtrail-logs"
  }
}

# CloudWatch Dashboards
resource "aws_cloudwatch_dashboard" "executive" {
  dashboard_name = "${var.project_name}-executive-dashboard"

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
            ["AWS/Organizations", "AccountCount", "OrganizationId", aws_organizations_organization.main.id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Total Accounts"
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
            ["AWS/CloudTrail", "CallCount", "LogGroupName", aws_cloudwatch_log_group.cloudtrail.name]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "API Calls"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_dashboard" "security" {
  dashboard_name = "${var.project_name}-security-dashboard"

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
            ["AWS/Config", "ConfigRuleEvaluations", "RuleName", "AWS-Config-Rule"]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Config Rule Evaluations"
        }
      }
    ]
  })
}

# SNS Topics for alerts
resource "aws_sns_topic" "landing_zone_alerts" {
  name = "${var.project_name}-landing-zone-alerts"
  
  tags = {
    Name = "${var.project_name}-landing-zone-alerts"
  }
}

resource "aws_sns_topic" "security_alerts" {
  name = "${var.project_name}-security-alerts"
  
  tags = {
    Name = "${var.project_name}-security-alerts"
  }
}

resource "aws_sns_topic" "compliance_alerts" {
  name = "${var.project_name}-compliance-alerts"
  
  tags = {
    Name = "${var.project_name}-compliance-alerts"
  }
}

# Budget alerts
resource "aws_budgets_budget" "monthly" {
  name              = "${var.project_name}-monthly-budget"
  budget_type       = "COST"
  time_unit         = "MONTHLY"
  limit_amount      = "1000"
  limit_unit        = "USD"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = [var.admin_email]
  }
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = [var.admin_email]
  }
}

# Service Control Policies (SCPs)
resource "aws_organizations_policy" "deny_root_user" {
  name = "${var.project_name}-deny-root-user"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:PrincipalType": "Root"
          }
        }
      }
    ]
  })
}

resource "aws_organizations_policy" "require_mfa" {
  name = "${var.project_name}-require-mfa"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent": "false"
          }
        }
      }
    ]
  })
}

# Attach SCPs to OUs
resource "aws_organizations_policy_attachment" "deny_root_user_security" {
  policy_id = aws_organizations_policy.deny_root_user.id
  target_id = aws_organizations_organizational_unit.security.id
}

resource "aws_organizations_policy_attachment" "deny_root_user_infrastructure" {
  policy_id = aws_organizations_policy.deny_root_user.id
  target_id = aws_organizations_organizational_unit.infrastructure.id
}

resource "aws_organizations_policy_attachment" "deny_root_user_workloads" {
  policy_id = aws_organizations_policy.deny_root_user.id
  target_id = aws_organizations_organizational_unit.workloads.id
}

resource "aws_organizations_policy_attachment" "require_mfa_security" {
  policy_id = aws_organizations_policy.require_mfa.id
  target_id = aws_organizations_organizational_unit.security.id
}

resource "aws_organizations_policy_attachment" "require_mfa_infrastructure" {
  policy_id = aws_organizations_policy.require_mfa.id
  target_id = aws_organizations_organizational_unit.infrastructure.id
}

resource "aws_organizations_policy_attachment" "require_mfa_workloads" {
  policy_id = aws_organizations_policy.require_mfa.id
  target_id = aws_organizations_organizational_unit.workloads.id
}
