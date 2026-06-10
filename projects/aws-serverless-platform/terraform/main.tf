terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "aws-serverless-platform-terraform-state"
    key            = "serverless-platform/terraform.tfstate"
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
      Component   = "ServerlessPlatform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS key for encryption
resource "aws_kms_key" "serverless_encryption" {
  description             = "KMS key for serverless platform encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-serverless-encryption"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "serverless_encryption" {
  name          = "alias/${var.project_name}-serverless-encryption"
  target_key_id = aws_kms_key.serverless_encryption.key_id
}

# IAM roles for Lambda functions
resource "aws_iam_role" "lambda_execution_role" {
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

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Custom Lambda execution policy
resource "aws_iam_role_policy" "lambda_custom_policy" {
  name = "${var.project_name}-lambda-custom-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:*",
          "s3:*",
          "sqs:*",
          "sns:*",
          "stepfunctions:*",
          "apigateway:*",
          "logs:*",
          "cloudwatch:*",
          "xray:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM role for Step Functions
resource "aws_iam_role" "stepfunctions_execution_role" {
  name = "${var.project_name}-stepfunctions-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-stepfunctions-execution-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "stepfunctions_execution_policy" {
  name = "${var.project_name}-stepfunctions-execution-policy"
  role = aws_iam_role.stepfunctions_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync",
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sns:Publish",
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# DynamoDB tables
resource "aws_dynamodb_table" "users" {
  count          = var.create_dynamodb_tables ? 1 : 0
  name           = "${var.project_name}-users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "email"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  global_secondary_index {
    name     = "email-index"
    hash_key = "email"
  }

  global_secondary_index {
    name     = "created-at-index"
    hash_key = "created_at"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.serverless_encryption.arn
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Name        = "${var.project_name}-users"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "orders" {
  count          = var.create_dynamodb_tables ? 1 : 0
  name           = "${var.project_name}-orders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "order_id"
  range_key      = "user_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  global_secondary_index {
    name     = "user-orders-index"
    hash_key = "user_id"
    range_key = "created_at"
  }

  global_secondary_index {
    name     = "status-index"
    hash_key = "status"
    range_key = "created_at"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.serverless_encryption.arn
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Name        = "${var.project_name}-orders"
    Environment = var.environment
  }
}

# SQS queues
resource "aws_sqs_queue" "order_processing" {
  count = var.create_sqs_queues ? 1 : 0
  name  = "${var.project_name}-order-processing"

  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600
  max_message_size          = 262144
  delay_seconds             = 0
  receive_wait_time_seconds = 20

  kms_master_key_id = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-order-processing"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "order_processing_dlq" {
  count = var.create_sqs_queues ? 1 : 0
  name  = "${var.project_name}-order-processing-dlq"

  message_retention_seconds = 1209600
  max_message_size         = 262144

  kms_master_key_id = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-order-processing-dlq"
    Environment = var.environment
  }
}

resource "aws_sqs_queue_redrive_policy" "order_processing" {
  count = var.create_sqs_queues ? 1 : 0
  queue_url = aws_sqs_queue.order_processing[0].id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_processing_dlq[0].arn
    maxReceiveCount     = 3
  })
}

# SNS topics
resource "aws_sns_topic" "order_notifications" {
  count = var.create_sns_topics ? 1 : 0
  name  = "${var.project_name}-order-notifications"

  kms_master_key_id = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-order-notifications"
    Environment = var.environment
  }
}

resource "aws_sns_topic" "system_alerts" {
  count = var.create_sns_topics ? 1 : 0
  name  = "${var.project_name}-system-alerts"

  kms_master_key_id = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-system-alerts"
    Environment = var.environment
  }
}

# Lambda functions
resource "aws_lambda_function" "order_processor" {
  count = var.create_lambda_functions ? 1 : 0
  filename         = "order_processor.zip"
  function_name    = "${var.project_name}-order-processor"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_TABLE = var.create_dynamodb_tables ? aws_dynamodb_table.users[0].name : ""
      SNS_TOPIC_ARN  = var.create_sns_topics ? aws_sns_topic.order_notifications[0].arn : ""
    }
  }

  vpc_config {
    subnet_ids         = var.vpc_subnet_ids
    security_group_ids = [aws_security_group.lambda[0].id]
  }

  dead_letter_config {
    target_arn = var.create_sqs_queues ? aws_sqs_queue.order_processing_dlq[0].arn : ""
  }

  tracing_config {
    mode = "Active"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = {
    Name        = "${var.project_name}-order-processor"
    Environment = var.environment
  }
}

resource "aws_lambda_function" "notification_sender" {
  count = var.create_lambda_functions ? 1 : 0
  filename         = "notification_sender.zip"
  function_name    = "${var.project_name}-notification-sender"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 60
  memory_size     = 128

  environment {
    variables = {
      SNS_TOPIC_ARN = var.create_sns_topics ? aws_sns_topic.order_notifications[0].arn : ""
    }
  }

  tracing_config {
    mode = "Active"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = {
    Name        = "${var.project_name}-notification-sender"
    Environment = var.environment
  }
}

# Step Functions state machine
resource "aws_sfn_state_machine" "order_workflow" {
  count = var.create_step_functions ? 1 : 0
  name     = "${var.project_name}-order-workflow"
  role_arn = aws_iam_role.stepfunctions_execution_role.arn

  definition = jsonencode({
    Comment = "Order processing workflow"
    StartAt = "ProcessOrder"
    States = {
      ProcessOrder = {
        Type     = "Task"
        Resource = var.create_lambda_functions ? aws_lambda_function.order_processor[0].arn : ""
        Next     = "SendNotification"
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts = 6
            BackoffRate = 2
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next = "HandleError"
          }
        ]
      }
      SendNotification = {
        Type     = "Task"
        Resource = var.create_lambda_functions ? aws_lambda_function.notification_sender[0].arn : ""
        End     = true
        Retry = [
          {
            ErrorEquals = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts = 6
            BackoffRate = 2
          }
        ]
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next = "HandleError"
          }
        ]
      }
      HandleError = {
        Type = "Fail"
        Cause = "Order processing failed"
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.stepfunctions[0].arn}:*"
    include_execution_data = true
    level                  = "ERROR"
  }

  tracing_configuration {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-order-workflow"
    Environment = var.environment
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "serverless_api" {
  count = var.create_api_gateway ? 1 : 0
  name        = "${var.project_name}-api"
  description = "Serverless platform API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}

resource "aws_api_gateway_resource" "orders" {
  count       = var.create_api_gateway ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.serverless_api[0].id
  parent_id   = aws_api_gateway_rest_api.serverless_api[0].root_resource_id
  path_part   = "orders"
}

resource "aws_api_gateway_method" "orders_post" {
  count         = var.create_api_gateway ? 1 : 0
  rest_api_id   = aws_api_gateway_rest_api.serverless_api[0].id
  resource_id   = aws_api_gateway_resource.orders[0].id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "orders_post" {
  count                   = var.create_api_gateway ? 1 : 0
  rest_api_id             = aws_api_gateway_rest_api.serverless_api[0].id
  resource_id             = aws_api_gateway_resource.orders[0].id
  http_method             = aws_api_gateway_method.orders_post[0].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.create_lambda_functions ? aws_lambda_function.order_processor[0].invoke_arn : ""
}

resource "aws_lambda_permission" "api_gateway_lambda" {
  count         = var.create_api_gateway && var.create_lambda_functions ? 1 : 0
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_processor[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.serverless_api[0].execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "serverless_api" {
  count       = var.create_api_gateway ? 1 : 0
  depends_on  = [aws_api_gateway_integration.orders_post]
  rest_api_id = aws_api_gateway_rest_api.serverless_api[0].id
  stage_name  = "prod"

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count             = var.create_lambda_functions ? 1 : 0
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-lambda-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "stepfunctions" {
  count             = var.create_step_functions ? 1 : 0
  name              = "/aws/stepfunctions/${var.project_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.serverless_encryption.arn

  tags = {
    Name        = "${var.project_name}-stepfunctions-logs"
    Environment = var.environment
  }
}

# Security Groups
resource "aws_security_group" "lambda" {
  count       = var.create_lambda_functions ? 1 : 0
  name        = "${var.project_name}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-lambda-sg"
    Environment = var.environment
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = var.create_lambda_functions ? 1 : 0
  alarm_name          = "${var.project_name}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda errors"
  alarm_actions       = var.create_sns_topics ? [aws_sns_topic.system_alerts[0].arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.order_processor[0].function_name
  }

  tags = {
    Name        = "${var.project_name}-lambda-errors"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_throttles" {
  count               = var.create_dynamodb_tables ? 1 : 0
  alarm_name          = "${var.project_name}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors dynamodb throttles"
  alarm_actions       = var.create_sns_topics ? [aws_sns_topic.system_alerts[0].arn] : []

  dimensions = {
    TableName = aws_dynamodb_table.users[0].name
  }

  tags = {
    Name        = "${var.project_name}-dynamodb-throttles"
    Environment = var.environment
  }
}

# SNS subscriptions
resource "aws_sns_topic_subscription" "email_notifications" {
  count     = var.create_sns_topics && var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.order_notifications[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

resource "aws_sns_topic_subscription" "system_alerts_email" {
  count     = var.create_sns_topics && var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.system_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# EventBridge rules
resource "aws_cloudwatch_event_rule" "order_processing_schedule" {
  count               = var.create_eventbridge_rules ? 1 : 0
  name                = "${var.project_name}-order-processing-schedule"
  description         = "Trigger order processing workflow"
  schedule_expression = "rate(5 minutes)"

  tags = {
    Name        = "${var.project_name}-order-processing-schedule"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "stepfunctions" {
  count     = var.create_eventbridge_rules && var.create_step_functions ? 1 : 0
  rule      = aws_cloudwatch_event_rule.order_processing_schedule[0].name
  target_id = "StepFunctionsTarget"
  arn       = aws_sfn_state_machine.order_workflow[0].arn
}

# X-Ray tracing
resource "aws_xray_sampling_rule" "serverless_tracing" {
  count = var.enable_xray_tracing ? 1 : 0
  rule_name      = "${var.project_name}-serverless-tracing"
  priority       = 10000
  version        = 1
  reservoir_size = 1
  fixed_rate     = 0.1
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"

  tags = {
    Name        = "${var.project_name}-serverless-tracing"
    Environment = var.environment
  }
}