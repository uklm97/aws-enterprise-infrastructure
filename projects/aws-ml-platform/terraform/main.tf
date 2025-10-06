terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "aws-ml-platform-terraform-state"
    key            = "ml-platform/terraform.tfstate"
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
      Component   = "MLPlatform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# S3 bucket for ML data and artifacts
resource "aws_s3_bucket" "ml_data" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = "${var.project_name}-ml-data-${random_string.bucket_suffix[0].result}"

  tags = {
    Name        = "${var.project_name}-ml-data"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "ml_data" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.ml_data[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_data" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.ml_data[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ml_data" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.ml_data[0].id

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

# SageMaker execution role
resource "aws_iam_role" "sagemaker_execution_role" {
  count = var.create_iam_roles ? 1 : 0
  name  = "${var.project_name}-sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-sagemaker-execution-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_policy" {
  count      = var.create_iam_roles ? 1 : 0
  role       = aws_iam_role.sagemaker_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_s3_policy" {
  count      = var.create_iam_roles ? 1 : 0
  role       = aws_iam_role.sagemaker_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_ecr_policy" {
  count      = var.create_iam_roles ? 1 : 0
  role       = aws_iam_role.sagemaker_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

# SageMaker domain
resource "aws_sagemaker_domain" "ml_domain" {
  count = var.create_sagemaker_domain ? 1 : 0
  domain_name = "${var.project_name}-domain"
  auth_mode   = "IAM"
  vpc_id      = var.vpc_id
  subnet_ids  = var.subnet_ids

  default_user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role[0].arn
  }

  tags = {
    Name        = "${var.project_name}-domain"
    Environment = var.environment
  }
}

# SageMaker user profile
resource "aws_sagemaker_user_profile" "ml_user_profile" {
  count = var.create_sagemaker_domain ? 1 : 0
  domain_id         = aws_sagemaker_domain.ml_domain[0].id
  user_profile_name = "${var.project_name}-user-profile"

  user_settings {
    execution_role = aws_iam_role.sagemaker_execution_role[0].arn
  }

  tags = {
    Name        = "${var.project_name}-user-profile"
    Environment = var.environment
  }
}

# SageMaker notebook instance
resource "aws_sagemaker_notebook_instance" "ml_notebook" {
  count = var.create_notebook_instance ? 1 : 0
  name          = "${var.project_name}-notebook"
  role_arn      = aws_iam_role.sagemaker_execution_role[0].arn
  instance_type = var.notebook_instance_type

  tags = {
    Name        = "${var.project_name}-notebook"
    Environment = var.environment
  }
}

# SageMaker model package group
resource "aws_sagemaker_model_package_group" "ml_models" {
  count = var.create_model_package_group ? 1 : 0
  model_package_group_name        = "${var.project_name}-models"
  model_package_group_description = "ML model package group for ${var.project_name}"

  tags = {
    Name        = "${var.project_name}-models"
    Environment = var.environment
  }
}

# SageMaker experiment
resource "aws_sagemaker_experiment" "ml_experiment" {
  count = var.create_experiment ? 1 : 0
  experiment_name = "${var.project_name}-experiment"
  display_name    = "${var.project_name} Experiment"
  description     = "Main experiment for ${var.project_name}"

  tags = {
    Name        = "${var.project_name}-experiment"
    Environment = var.environment
  }
}

# SageMaker pipeline
resource "aws_sagemaker_pipeline" "ml_pipeline" {
  count = var.create_pipeline ? 1 : 0
  pipeline_name        = "${var.project_name}-pipeline"
  pipeline_display_name = "${var.project_name} Pipeline"
  pipeline_description = "ML pipeline for ${var.project_name}"
  pipeline_definition  = var.pipeline_definition

  tags = {
    Name        = "${var.project_name}-pipeline"
    Environment = var.environment
  }
}

# SageMaker endpoint configuration
resource "aws_sagemaker_endpoint_configuration" "ml_endpoint_config" {
  count = var.create_endpoint_configuration ? 1 : 0
  name = "${var.project_name}-endpoint-config"

  production_variants {
    variant_name           = "primary"
    model_name            = var.model_name
    initial_instance_count = var.initial_instance_count
    instance_type         = var.instance_type
    initial_variant_weight = 100
  }

  tags = {
    Name        = "${var.project_name}-endpoint-config"
    Environment = var.environment
  }
}

# SageMaker endpoint
resource "aws_sagemaker_endpoint" "ml_endpoint" {
  count = var.create_endpoint ? 1 : 0
  name                 = "${var.project_name}-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.ml_endpoint_config[0].name

  tags = {
    Name        = "${var.project_name}-endpoint"
    Environment = var.environment
  }
}

# SageMaker monitoring schedule
resource "aws_sagemaker_monitoring_schedule" "ml_monitoring" {
  count = var.create_monitoring_schedule ? 1 : 0
  name = "${var.project_name}-monitoring"

  monitoring_schedule_config {
    monitoring_job_definition_name = aws_sagemaker_data_quality_job_definition.ml_data_quality[0].name
    monitoring_type                = "DataQuality"
    schedule_config {
      schedule_expression = var.monitoring_schedule_expression
    }
  }

  tags = {
    Name        = "${var.project_name}-monitoring"
    Environment = var.environment
  }
}

# SageMaker data quality job definition
resource "aws_sagemaker_data_quality_job_definition" "ml_data_quality" {
  count = var.create_data_quality_job ? 1 : 0
  name = "${var.project_name}-data-quality"

  data_quality_app_specification {
    image_uri = var.data_quality_image_uri
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name = aws_sagemaker_endpoint.ml_endpoint[0].name
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri = "s3://${aws_s3_bucket.ml_data[0].bucket}/monitoring/data-quality"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count    = 1
      instance_type     = "ml.m5.large"
      volume_size_in_gb = 30
    }
  }

  role_arn = aws_iam_role.sagemaker_execution_role[0].arn

  tags = {
    Name        = "${var.project_name}-data-quality"
    Environment = var.environment
  }
}

# SageMaker model quality job definition
resource "aws_sagemaker_model_quality_job_definition" "ml_model_quality" {
  count = var.create_model_quality_job ? 1 : 0
  name = "${var.project_name}-model-quality"

  model_quality_app_specification {
    image_uri = var.model_quality_image_uri
  }

  model_quality_job_input {
    endpoint_input {
      endpoint_name = aws_sagemaker_endpoint.ml_endpoint[0].name
    }
  }

  model_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri = "s3://${aws_s3_bucket.ml_data[0].bucket}/monitoring/model-quality"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count    = 1
      instance_type     = "ml.m5.large"
      volume_size_in_gb = 30
    }
  }

  role_arn = aws_iam_role.sagemaker_execution_role[0].arn

  tags = {
    Name        = "${var.project_name}-model-quality"
    Environment = var.environment
  }
}

# SageMaker bias job definition
resource "aws_sagemaker_model_bias_job_definition" "ml_bias" {
  count = var.create_bias_job ? 1 : 0
  name = "${var.project_name}-bias"

  model_bias_app_specification {
    image_uri = var.bias_image_uri
  }

  model_bias_job_input {
    endpoint_input {
      endpoint_name = aws_sagemaker_endpoint.ml_endpoint[0].name
    }
  }

  model_bias_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri = "s3://${aws_s3_bucket.ml_data[0].bucket}/monitoring/bias"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count    = 1
      instance_type     = "ml.m5.large"
      volume_size_in_gb = 30
    }
  }

  role_arn = aws_iam_role.sagemaker_execution_role[0].arn

  tags = {
    Name        = "${var.project_name}-bias"
    Environment = var.environment
  }
}

# SageMaker explainability job definition
resource "aws_sagemaker_model_explainability_job_definition" "ml_explainability" {
  count = var.create_explainability_job ? 1 : 0
  name = "${var.project_name}-explainability"

  model_explainability_app_specification {
    image_uri = var.explainability_image_uri
  }

  model_explainability_job_input {
    endpoint_input {
      endpoint_name = aws_sagemaker_endpoint.ml_endpoint[0].name
    }
  }

  model_explainability_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri = "s3://${aws_s3_bucket.ml_data[0].bucket}/monitoring/explainability"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count    = 1
      instance_type     = "ml.m5.large"
      volume_size_in_gb = 30
    }
  }

  role_arn = aws_iam_role.sagemaker_execution_role[0].arn

  tags = {
    Name        = "${var.project_name}-explainability"
    Environment = var.environment
  }
}

# ECR repository for ML containers
resource "aws_ecr_repository" "ml_repository" {
  count = var.create_ecr_repository ? 1 : 0
  name                 = "${var.project_name}-ml"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-ml"
    Environment = var.environment
  }
}

# ECR lifecycle policy
resource "aws_ecr_lifecycle_policy" "ml_repository_policy" {
  count = var.create_ecr_repository ? 1 : 0
  repository = aws_ecr_repository.ml_repository[0].name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Lambda function for ML automation
resource "aws_lambda_function" "ml_automation" {
  count = var.create_lambda_functions ? 1 : 0
  filename         = "ml_automation.zip"
  function_name    = "${var.project_name}-ml-automation"
  role            = aws_iam_role.lambda_execution_role[0].arn
  handler         = "ml_automation.handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      SAGEMAKER_ROLE_ARN = aws_iam_role.sagemaker_execution_role[0].arn
      S3_BUCKET = var.create_s3_bucket ? aws_s3_bucket.ml_data[0].bucket : ""
      ECR_REPOSITORY = var.create_ecr_repository ? aws_ecr_repository.ml_repository[0].repository_url : ""
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_policy,
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = {
    Name        = "${var.project_name}-ml-automation"
    Environment = var.environment
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  count = var.create_lambda_functions ? 1 : 0
  name = "${var.project_name}-lambda-execution-role"

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
    Name        = "${var.project_name}-lambda-execution-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  count      = var.create_lambda_functions ? 1 : 0
  role       = aws_iam_role.lambda_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_sagemaker_policy" {
  count = var.create_lambda_functions ? 1 : 0
  name  = "${var.project_name}-lambda-sagemaker-policy"
  role  = aws_iam_role.lambda_execution_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sagemaker:*",
          "s3:*",
          "ecr:*",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count             = var.create_lambda_functions ? 1 : 0
  name              = "/aws/lambda/${var.project_name}-ml-automation"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-lambda-logs"
    Environment = var.environment
  }
}

# EventBridge rules for ML automation
resource "aws_cloudwatch_event_rule" "ml_automation_rule" {
  count = var.create_eventbridge_rules ? 1 : 0
  name  = "${var.project_name}-ml-automation-rule"

  description = "ML automation trigger"
  schedule_expression = var.automation_schedule_expression

  tags = {
    Name        = "${var.project_name}-ml-automation-rule"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "ml_automation_target" {
  count     = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  rule      = aws_cloudwatch_event_rule.ml_automation_rule[0].name
  target_id = "MLAutomationTarget"
  arn       = aws_lambda_function.ml_automation[0].arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  count         = var.create_eventbridge_rules && var.create_lambda_functions ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ml_automation[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ml_automation_rule[0].arn
}

# CloudWatch dashboard for ML monitoring
resource "aws_cloudwatch_dashboard" "ml_dashboard" {
  count = var.create_dashboard ? 1 : 0
  dashboard_name = "${var.project_name}-ml-dashboard"

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
            ["AWS/SageMaker", "TrainingJobStatus", "TrainingJobName", ".*"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Training Job Status"
          period  = 300
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
            ["AWS/SageMaker", "Invocations", "EndpointName", ".*"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Endpoint Invocations"
          period  = 300
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-ml-dashboard"
    Environment = var.environment
  }
}

# SNS topic for ML notifications
resource "aws_sns_topic" "ml_notifications" {
  count = var.create_sns_topic ? 1 : 0
  name  = "${var.project_name}-ml-notifications"

  tags = {
    Name        = "${var.project_name}-ml-notifications"
    Environment = var.environment
  }
}

# SNS subscription
resource "aws_sns_topic_subscription" "ml_notifications_email" {
  count     = var.create_sns_topic && var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.ml_notifications[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# API Gateway for ML endpoints
resource "aws_api_gateway_rest_api" "ml_api" {
  count = var.create_api_gateway ? 1 : 0
  name        = "${var.project_name}-ml-api"
  description = "ML Platform API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-ml-api"
    Environment = var.environment
  }
}

resource "aws_api_gateway_resource" "ml_predict" {
  count       = var.create_api_gateway ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.ml_api[0].id
  parent_id   = aws_api_gateway_rest_api.ml_api[0].root_resource_id
  path_part   = "predict"
}

resource "aws_api_gateway_method" "ml_predict_post" {
  count         = var.create_api_gateway ? 1 : 0
  rest_api_id   = aws_api_gateway_rest_api.ml_api[0].id
  resource_id   = aws_api_gateway_resource.ml_predict[0].id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "ml_predict_integration" {
  count                   = var.create_api_gateway ? 1 : 0
  rest_api_id             = aws_api_gateway_rest_api.ml_api[0].id
  resource_id             = aws_api_gateway_resource.ml_predict[0].id
  http_method             = aws_api_gateway_method.ml_predict_post[0].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ml_automation[0].invoke_arn
}

resource "aws_api_gateway_deployment" "ml_api_deployment" {
  count       = var.create_api_gateway ? 1 : 0
  depends_on  = [aws_api_gateway_integration.ml_predict_integration]
  rest_api_id = aws_api_gateway_rest_api.ml_api[0].id
  stage_name  = "prod"
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_lambda" {
  count         = var.create_api_gateway && var.create_lambda_functions ? 1 : 0
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ml_automation[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ml_api[0].execution_arn}/*/*"
}