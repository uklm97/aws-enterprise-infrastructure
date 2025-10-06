output "s3_bucket" {
  description = "S3 bucket for ML data and artifacts"
  value = {
    bucket = var.create_s3_bucket ? {
      name = aws_s3_bucket.ml_data[0].bucket
      arn = aws_s3_bucket.ml_data[0].arn
      region = aws_s3_bucket.ml_data[0].region
    } : null
  }
}

output "sagemaker_domain" {
  description = "SageMaker domain information"
  value = {
    domain = var.create_sagemaker_domain ? {
      id = aws_sagemaker_domain.ml_domain[0].id
      arn = aws_sagemaker_domain.ml_domain[0].arn
      url = aws_sagemaker_domain.ml_domain[0].url
    } : null
    user_profile = var.create_sagemaker_domain ? {
      id = aws_sagemaker_user_profile.ml_user_profile[0].id
      arn = aws_sagemaker_user_profile.ml_user_profile[0].arn
    } : null
  }
}

output "sagemaker_notebook" {
  description = "SageMaker notebook instance"
  value = {
    notebook = var.create_notebook_instance ? {
      name = aws_sagemaker_notebook_instance.ml_notebook[0].name
      arn = aws_sagemaker_notebook_instance.ml_notebook[0].arn
      instance_type = aws_sagemaker_notebook_instance.ml_notebook[0].instance_type
    } : null
  }
}

output "sagemaker_experiment" {
  description = "SageMaker experiment"
  value = {
    experiment = var.create_experiment ? {
      name = aws_sagemaker_experiment.ml_experiment[0].experiment_name
      arn = aws_sagemaker_experiment.ml_experiment[0].arn
    } : null
  }
}

output "sagemaker_pipeline" {
  description = "SageMaker pipeline"
  value = {
    pipeline = var.create_pipeline ? {
      name = aws_sagemaker_pipeline.ml_pipeline[0].pipeline_name
      arn = aws_sagemaker_pipeline.ml_pipeline[0].arn
    } : null
  }
}

output "sagemaker_endpoint" {
  description = "SageMaker endpoint"
  value = {
    endpoint = var.create_endpoint ? {
      name = aws_sagemaker_endpoint.ml_endpoint[0].name
      arn = aws_sagemaker_endpoint.ml_endpoint[0].arn
      url = "https://runtime.sagemaker.${var.aws_region}.amazonaws.com/endpoints/${aws_sagemaker_endpoint.ml_endpoint[0].name}/invocations"
    } : null
    endpoint_config = var.create_endpoint_configuration ? {
      name = aws_sagemaker_endpoint_configuration.ml_endpoint_config[0].name
      arn = aws_sagemaker_endpoint_configuration.ml_endpoint_config[0].arn
    } : null
  }
}

output "sagemaker_monitoring" {
  description = "SageMaker monitoring configuration"
  value = {
    monitoring_schedule = var.create_monitoring_schedule ? {
      name = aws_sagemaker_monitoring_schedule.ml_monitoring[0].name
      arn = aws_sagemaker_monitoring_schedule.ml_monitoring[0].arn
    } : null
    data_quality_job = var.create_data_quality_job ? {
      name = aws_sagemaker_data_quality_job_definition.ml_data_quality[0].name
      arn = aws_sagemaker_data_quality_job_definition.ml_data_quality[0].arn
    } : null
    model_quality_job = var.create_model_quality_job ? {
      name = aws_sagemaker_model_quality_job_definition.ml_model_quality[0].name
      arn = aws_sagemaker_model_quality_job_definition.ml_model_quality[0].arn
    } : null
    bias_job = var.create_bias_job ? {
      name = aws_sagemaker_model_bias_job_definition.ml_bias[0].name
      arn = aws_sagemaker_model_bias_job_definition.ml_bias[0].arn
    } : null
    explainability_job = var.create_explainability_job ? {
      name = aws_sagemaker_model_explainability_job_definition.ml_explainability[0].name
      arn = aws_sagemaker_model_explainability_job_definition.ml_explainability[0].arn
    } : null
  }
}

output "model_package_group" {
  description = "SageMaker model package group"
  value = {
    package_group = var.create_model_package_group ? {
      name = aws_sagemaker_model_package_group.ml_models[0].model_package_group_name
      arn = aws_sagemaker_model_package_group.ml_models[0].arn
    } : null
  }
}

output "ecr_repository" {
  description = "ECR repository for ML containers"
  value = {
    repository = var.create_ecr_repository ? {
      name = aws_ecr_repository.ml_repository[0].name
      arn = aws_ecr_repository.ml_repository[0].arn
      url = aws_ecr_repository.ml_repository[0].repository_url
    } : null
  }
}

output "lambda_functions" {
  description = "Lambda functions for ML automation"
  value = {
    ml_automation = var.create_lambda_functions ? {
      name = aws_lambda_function.ml_automation[0].function_name
      arn = aws_lambda_function.ml_automation[0].arn
      role_arn = aws_iam_role.lambda_execution_role[0].arn
    } : null
  }
}

output "iam_roles" {
  description = "IAM roles for ML platform"
  value = {
    sagemaker_execution_role = var.create_iam_roles ? {
      name = aws_iam_role.sagemaker_execution_role[0].name
      arn = aws_iam_role.sagemaker_execution_role[0].arn
    } : null
    lambda_execution_role = var.create_lambda_functions ? {
      name = aws_iam_role.lambda_execution_role[0].name
      arn = aws_iam_role.lambda_execution_role[0].arn
    } : null
  }
}

output "eventbridge_rules" {
  description = "EventBridge rules for ML automation"
  value = {
    ml_automation_rule = var.create_eventbridge_rules ? {
      name = aws_cloudwatch_event_rule.ml_automation_rule[0].name
      arn = aws_cloudwatch_event_rule.ml_automation_rule[0].arn
      schedule = aws_cloudwatch_event_rule.ml_automation_rule[0].schedule_expression
    } : null
  }
}

output "cloudwatch_dashboard" {
  description = "CloudWatch dashboard for ML monitoring"
  value = {
    dashboard = var.create_dashboard ? {
      name = aws_cloudwatch_dashboard.ml_dashboard[0].dashboard_name
      url = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.ml_dashboard[0].dashboard_name}"
    } : null
  }
}

output "sns_topic" {
  description = "SNS topic for ML notifications"
  value = {
    topic = var.create_sns_topic ? {
      name = aws_sns_topic.ml_notifications[0].name
      arn = aws_sns_topic.ml_notifications[0].arn
    } : null
  }
}

output "api_gateway" {
  description = "API Gateway for ML endpoints"
  value = {
    api = var.create_api_gateway ? {
      name = aws_api_gateway_rest_api.ml_api[0].name
      id = aws_api_gateway_rest_api.ml_api[0].id
      url = "https://${aws_api_gateway_rest_api.ml_api[0].id}.execute-api.${var.aws_region}.amazonaws.com/prod"
    } : null
  }
}

output "monitoring_endpoints" {
  description = "Monitoring and management endpoints"
  value = {
    sagemaker_console = "https://console.aws.amazon.com/sagemaker/home?region=${var.aws_region}"
    sagemaker_studio = var.create_sagemaker_domain ? "https://${aws_sagemaker_domain.ml_domain[0].url}" : ""
    cloudwatch_dashboard = var.create_dashboard ? "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.ml_dashboard[0].dashboard_name}" : ""
    ecr_console = "https://console.aws.amazon.com/ecr/repositories?region=${var.aws_region}"
    s3_console = var.create_s3_bucket ? "https://console.aws.amazon.com/s3/buckets/${aws_s3_bucket.ml_data[0].bucket}?region=${var.aws_region}" : ""
  }
}

output "configuration_summary" {
  description = "ML platform configuration summary"
  value = {
    project_name = var.project_name
    environment = var.environment
    region = var.aws_region
    model_framework = var.model_framework
    model_version = var.model_version
    python_version = var.python_version
    features_enabled = {
      sagemaker_domain = var.create_sagemaker_domain
      notebook_instance = var.create_notebook_instance
      experiment_tracking = var.create_experiment
      model_pipeline = var.create_pipeline
      endpoint = var.create_endpoint
      monitoring = var.create_monitoring_schedule
      data_quality = var.create_data_quality_job
      model_quality = var.create_model_quality_job
      bias_monitoring = var.create_bias_job
      explainability = var.create_explainability_job
      ecr_repository = var.create_ecr_repository
      lambda_automation = var.create_lambda_functions
      eventbridge_rules = var.create_eventbridge_rules
      cloudwatch_dashboard = var.create_dashboard
      sns_notifications = var.create_sns_topic
      api_gateway = var.create_api_gateway
    }
  }
}

output "ml_platform_capabilities" {
  description = "Available ML platform capabilities"
  value = {
    model_training = "SageMaker training jobs with hyperparameter tuning"
    model_deployment = "Real-time and batch inference endpoints"
    experiment_tracking = "Comprehensive experiment tracking and comparison"
    model_monitoring = "Data quality, model quality, bias, and explainability monitoring"
    mlops_automation = "Automated ML workflows and CI/CD pipelines"
    model_registry = "Model versioning and lifecycle management"
    data_processing = "Data preprocessing and feature engineering"
    hyperparameter_tuning = "Automated hyperparameter optimization"
    automated_ml = "AutoML capabilities for model selection"
    batch_inference = "Large-scale batch inference processing"
    real_time_inference = "Low-latency real-time inference"
    model_explainability = "Model interpretability and explainability"
    bias_detection = "Fairness and bias monitoring"
    cost_optimization = "Spot training and cost-effective inference"
    security = "Encryption, network isolation, and access control"
  }
}

output "next_steps" {
  description = "Recommended next steps for ML platform"
  value = [
    "1. Access SageMaker Studio to start developing ML models",
    "2. Upload your training data to the S3 bucket",
    "3. Create your first experiment and start tracking runs",
    "4. Set up model monitoring for production endpoints",
    "5. Configure automated retraining workflows",
    "6. Set up model approval and deployment pipelines",
    "7. Configure cost optimization settings",
    "8. Set up notifications for model performance alerts",
    "9. Create custom monitoring dashboards",
    "10. Implement model versioning and lifecycle management"
  ]
}

output "ml_platform_features" {
  description = "ML platform feature highlights"
  value = {
    experiment_tracking = "Track experiments, compare models, and manage hyperparameters"
    model_training = "Distributed training with SageMaker built-in algorithms and custom containers"
    model_deployment = "Deploy models to real-time endpoints or batch processing jobs"
    model_monitoring = "Monitor data drift, model performance, bias, and explainability"
    mlops_automation = "Automated ML workflows with CI/CD integration"
    cost_optimization = "Spot training, managed spot training, and cost-effective inference"
    security = "End-to-end encryption, network isolation, and IAM-based access control"
    scalability = "Auto-scaling endpoints and distributed training capabilities"
    monitoring = "Comprehensive monitoring with CloudWatch integration"
    compliance = "Built-in compliance features for regulated industries"
  }
}

output "api_endpoints" {
  description = "API endpoints for ML platform"
  value = {
    predict_endpoint = var.create_api_gateway ? "https://${aws_api_gateway_rest_api.ml_api[0].id}.execute-api.${var.aws_region}.amazonaws.com/prod/predict" : ""
    sagemaker_endpoint = var.create_endpoint ? "https://runtime.sagemaker.${var.aws_region}.amazonaws.com/endpoints/${aws_sagemaker_endpoint.ml_endpoint[0].name}/invocations" : ""
  }
}

output "data_storage" {
  description = "Data storage information"
  value = {
    s3_bucket = var.create_s3_bucket ? {
      name = aws_s3_bucket.ml_data[0].bucket
      region = aws_s3_bucket.ml_data[0].region
      encryption = "AES256"
    } : null
    ecr_repository = var.create_ecr_repository ? {
      name = aws_ecr_repository.ml_repository[0].name
      url = aws_ecr_repository.ml_repository[0].repository_url
    } : null
  }
}

output "monitoring_configuration" {
  description = "Monitoring configuration details"
  value = {
    cloudwatch_dashboard = var.create_dashboard ? {
      name = aws_cloudwatch_dashboard.ml_dashboard[0].dashboard_name
      url = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.ml_dashboard[0].dashboard_name}"
    } : null
    monitoring_schedule = var.create_monitoring_schedule ? {
      expression = aws_sagemaker_monitoring_schedule.ml_monitoring[0].monitoring_schedule_config[0].schedule_config[0].schedule_expression
    } : null
    sns_notifications = var.create_sns_topic ? {
      topic_arn = aws_sns_topic.ml_notifications[0].arn
    } : null
  }
}

output "automation_workflows" {
  description = "Automation workflow configuration"
  value = {
    eventbridge_rule = var.create_eventbridge_rules ? {
      name = aws_cloudwatch_event_rule.ml_automation_rule[0].name
      schedule = aws_cloudwatch_event_rule.ml_automation_rule[0].schedule_expression
    } : null
    lambda_function = var.create_lambda_functions ? {
      name = aws_lambda_function.ml_automation[0].function_name
      arn = aws_lambda_function.ml_automation[0].arn
    } : null
  }
}

output "security_configuration" {
  description = "Security configuration details"
  value = {
    encryption_enabled = var.enable_encryption
    network_isolation = var.enable_network_isolation
    inter_container_encryption = var.enable_inter_container_traffic_encryption
    kms_key_id = var.kms_key_id
    iam_roles = var.create_iam_roles ? {
      sagemaker_role = aws_iam_role.sagemaker_execution_role[0].arn
      lambda_role = var.create_lambda_functions ? aws_iam_role.lambda_execution_role[0].arn : null
    } : null
  }
}

output "cost_optimization" {
  description = "Cost optimization features"
  value = {
    spot_training_enabled = var.enable_spot_training
    managed_spot_training = var.enable_managed_spot_training
    max_wait_time = var.max_wait_time
    auto_scaling = var.auto_scaling_enabled
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
    target_utilization = var.target_utilization
  }
}