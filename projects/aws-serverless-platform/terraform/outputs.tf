output "kms_key_id" {
  description = "KMS key ID for encryption"
  value       = aws_kms_key.serverless_encryption.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for encryption"
  value       = aws_kms_key.serverless_encryption.arn
}

output "kms_alias_arn" {
  description = "KMS alias ARN for encryption"
  value       = aws_kms_alias.serverless_encryption.arn
}

# DynamoDB outputs
output "dynamodb_tables" {
  description = "DynamoDB table information"
  value = {
    users = var.create_dynamodb_tables ? {
      name = aws_dynamodb_table.users[0].name
      arn  = aws_dynamodb_table.users[0].arn
      id   = aws_dynamodb_table.users[0].id
    } : null
    orders = var.create_dynamodb_tables ? {
      name = aws_dynamodb_table.orders[0].name
      arn  = aws_dynamodb_table.orders[0].arn
      id   = aws_dynamodb_table.orders[0].id
    } : null
  }
}

output "dynamodb_table_arns" {
  description = "DynamoDB table ARNs"
  value = var.create_dynamodb_tables ? [
    aws_dynamodb_table.users[0].arn,
    aws_dynamodb_table.orders[0].arn
  ] : []
}

# SQS outputs
output "sqs_queues" {
  description = "SQS queue information"
  value = {
    order_processing = var.create_sqs_queues ? {
      url = aws_sqs_queue.order_processing[0].url
      arn = aws_sqs_queue.order_processing[0].arn
      id  = aws_sqs_queue.order_processing[0].id
    } : null
    order_processing_dlq = var.create_sqs_queues ? {
      url = aws_sqs_queue.order_processing_dlq[0].url
      arn = aws_sqs_queue.order_processing_dlq[0].arn
      id  = aws_sqs_queue.order_processing_dlq[0].id
    } : null
  }
}

output "sqs_queue_urls" {
  description = "SQS queue URLs"
  value = var.create_sqs_queues ? [
    aws_sqs_queue.order_processing[0].url,
    aws_sqs_queue.order_processing_dlq[0].url
  ] : []
}

# SNS outputs
output "sns_topics" {
  description = "SNS topic information"
  value = {
    order_notifications = var.create_sns_topics ? {
      arn = aws_sns_topic.order_notifications[0].arn
      id  = aws_sns_topic.order_notifications[0].id
    } : null
    system_alerts = var.create_sns_topics ? {
      arn = aws_sns_topic.system_alerts[0].arn
      id  = aws_sns_topic.system_alerts[0].id
    } : null
  }
}

output "sns_topic_arns" {
  description = "SNS topic ARNs"
  value = var.create_sns_topics ? [
    aws_sns_topic.order_notifications[0].arn,
    aws_sns_topic.system_alerts[0].arn
  ] : []
}

# Lambda outputs
output "lambda_functions" {
  description = "Lambda function information"
  value = {
    order_processor = var.create_lambda_functions ? {
      name = aws_lambda_function.order_processor[0].function_name
      arn  = aws_lambda_function.order_processor[0].arn
      id   = aws_lambda_function.order_processor[0].id
    } : null
    notification_sender = var.create_lambda_functions ? {
      name = aws_lambda_function.notification_sender[0].function_name
      arn  = aws_lambda_function.notification_sender[0].arn
      id   = aws_lambda_function.notification_sender[0].id
    } : null
  }
}

output "lambda_function_arns" {
  description = "Lambda function ARNs"
  value = var.create_lambda_functions ? [
    aws_lambda_function.order_processor[0].arn,
    aws_lambda_function.notification_sender[0].arn
  ] : []
}

# Step Functions outputs
output "stepfunctions_state_machines" {
  description = "Step Functions state machine information"
  value = {
    order_workflow = var.create_step_functions ? {
      name = aws_sfn_state_machine.order_workflow[0].name
      arn  = aws_sfn_state_machine.order_workflow[0].arn
      id   = aws_sfn_state_machine.order_workflow[0].id
    } : null
  }
}

output "stepfunctions_state_machine_arns" {
  description = "Step Functions state machine ARNs"
  value = var.create_step_functions ? [
    aws_sfn_state_machine.order_workflow[0].arn
  ] : []
}

# API Gateway outputs
output "api_gateway" {
  description = "API Gateway information"
  value = var.create_api_gateway ? {
    id       = aws_api_gateway_rest_api.serverless_api[0].id
    arn      = aws_api_gateway_rest_api.serverless_api[0].arn
    name     = aws_api_gateway_rest_api.serverless_api[0].name
    endpoint = "https://${aws_api_gateway_rest_api.serverless_api[0].id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_deployment.serverless_api[0].stage_name}"
  } : null
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value = var.create_api_gateway ? "https://${aws_api_gateway_rest_api.serverless_api[0].id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_deployment.serverless_api[0].stage_name}" : ""
}

# CloudWatch outputs
output "cloudwatch_log_groups" {
  description = "CloudWatch log group information"
  value = {
    lambda_logs = var.create_lambda_functions ? {
      name = aws_cloudwatch_log_group.lambda_logs[0].name
      arn  = aws_cloudwatch_log_group.lambda_logs[0].arn
    } : null
    stepfunctions_logs = var.create_step_functions ? {
      name = aws_cloudwatch_log_group.stepfunctions[0].name
      arn  = aws_cloudwatch_log_group.stepfunctions[0].arn
    } : null
  }
}

output "cloudwatch_alarms" {
  description = "CloudWatch alarm information"
  value = {
    lambda_errors = var.create_cloudwatch_alarms && var.create_lambda_functions ? {
      name = aws_cloudwatch_metric_alarm.lambda_errors[0].alarm_name
      arn  = aws_cloudwatch_metric_alarm.lambda_errors[0].arn
    } : null
    dynamodb_throttles = var.create_cloudwatch_alarms && var.create_dynamodb_tables ? {
      name = aws_cloudwatch_metric_alarm.dynamodb_throttles[0].alarm_name
      arn  = aws_cloudwatch_metric_alarm.dynamodb_throttles[0].arn
    } : null
  }
}

# IAM outputs
output "iam_roles" {
  description = "IAM role information"
  value = {
    lambda_execution_role = {
      name = aws_iam_role.lambda_execution_role.name
      arn  = aws_iam_role.lambda_execution_role.arn
    }
    stepfunctions_execution_role = {
      name = aws_iam_role.stepfunctions_execution_role.name
      arn  = aws_iam_role.stepfunctions_execution_role.arn
    }
  }
}

# Security outputs
output "security_groups" {
  description = "Security group information"
  value = {
    lambda_sg = var.create_lambda_functions ? {
      id   = aws_security_group.lambda[0].id
      arn  = aws_security_group.lambda[0].arn
      name = aws_security_group.lambda[0].name
    } : null
  }
}

# EventBridge outputs
output "eventbridge_rules" {
  description = "EventBridge rule information"
  value = {
    order_processing_schedule = var.create_eventbridge_rules ? {
      name = aws_cloudwatch_event_rule.order_processing_schedule[0].name
      arn  = aws_cloudwatch_event_rule.order_processing_schedule[0].arn
    } : null
  }
}

# X-Ray outputs
output "xray_sampling_rule" {
  description = "X-Ray sampling rule information"
  value = var.enable_xray_tracing ? {
    name = aws_xray_sampling_rule.serverless_tracing[0].rule_name
    arn  = aws_xray_sampling_rule.serverless_tracing[0].arn
  } : null
}

# SNS subscription outputs
output "sns_subscriptions" {
  description = "SNS subscription information"
  value = {
    email_notifications = var.create_sns_topics && var.notification_email != "" ? {
      arn = aws_sns_topic_subscription.email_notifications[0].arn
    } : null
    system_alerts_email = var.create_sns_topics && var.alert_email != "" ? {
      arn = aws_sns_topic_subscription.system_alerts_email[0].arn
    } : null
  }
}

# Connection information
output "connection_info" {
  description = "Connection information for the serverless platform"
  value = {
    api_endpoint = var.create_api_gateway ? "https://${aws_api_gateway_rest_api.serverless_api[0].id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_deployment.serverless_api[0].stage_name}" : ""
    region      = var.aws_region
    account_id  = data.aws_caller_identity.current.account_id
  }
}

# Monitoring endpoints
output "monitoring_endpoints" {
  description = "Monitoring and observability endpoints"
  value = {
    cloudwatch_logs = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups"
    xray_tracing   = var.enable_xray_tracing ? "https://${var.aws_region}.console.aws.amazon.com/xray/home?region=${var.aws_region}#/traces" : ""
    stepfunctions  = var.create_step_functions ? "https://${var.aws_region}.console.aws.amazon.com/states/home?region=${var.aws_region}#/statemachines" : ""
  }
}

# Cost information
output "cost_estimation" {
  description = "Estimated monthly costs for the serverless platform"
  value = {
    dynamodb = var.create_dynamodb_tables ? "Pay-per-request pricing (varies by usage)" : "Not created"
    lambda   = var.create_lambda_functions ? "Pay-per-request pricing (varies by invocations and duration)" : "Not created"
    sqs      = var.create_sqs_queues ? "Pay-per-request pricing (varies by messages)" : "Not created"
    sns      = var.create_sns_topics ? "Pay-per-request pricing (varies by messages)" : "Not created"
    apigateway = var.create_api_gateway ? "Pay-per-request pricing (varies by API calls)" : "Not created"
    stepfunctions = var.create_step_functions ? "Pay-per-request pricing (varies by state transitions)" : "Not created"
  }
}

# Feature flags status
output "feature_flags_status" {
  description = "Status of feature flags"
  value = var.feature_flags
}

# Resource counts
output "resource_counts" {
  description = "Count of created resources"
  value = {
    dynamodb_tables = var.create_dynamodb_tables ? 2 : 0
    sqs_queues      = var.create_sqs_queues ? 2 : 0
    sns_topics      = var.create_sns_topics ? 2 : 0
    lambda_functions = var.create_lambda_functions ? 2 : 0
    stepfunctions_state_machines = var.create_step_functions ? 1 : 0
    api_gateways    = var.create_api_gateway ? 1 : 0
    cloudwatch_alarms = var.create_cloudwatch_alarms ? 2 : 0
    eventbridge_rules = var.create_eventbridge_rules ? 1 : 0
  }
}

# Deployment information
output "deployment_info" {
  description = "Deployment information"
  value = {
    terraform_version = ">= 1.0"
    aws_provider_version = "~> 5.0"
    region = var.aws_region
    environment = var.environment
    project_name = var.project_name
    created_at = timestamp()
  }
}