output "sns_topics" {
  description = "SNS topics for cost alerts and notifications"
  value = {
    cost_alerts = var.create_sns_topics ? {
      arn = aws_sns_topic.cost_alerts[0].arn
      name = aws_sns_topic.cost_alerts[0].name
    } : null
    budget_alerts = var.create_sns_topics ? {
      arn = aws_sns_topic.budget_alerts[0].arn
      name = aws_sns_topic.budget_alerts[0].name
    } : null
    optimization_reports = var.create_sns_topics ? {
      arn = aws_sns_topic.optimization_reports[0].arn
      name = aws_sns_topic.optimization_reports[0].name
    } : null
  }
}

output "budgets" {
  description = "Created budgets"
  value = {
    monthly_budget = var.create_budgets ? {
      name = aws_budgets_budget.monthly_budget[0].name
      limit = aws_budgets_budget.monthly_budget[0].limit_amount
      unit = aws_budgets_budget.monthly_budget[0].limit_unit
    } : null
    daily_budget = var.create_budgets ? {
      name = aws_budgets_budget.daily_budget[0].name
      limit = aws_budgets_budget.daily_budget[0].limit_amount
      unit = aws_budgets_budget.daily_budget[0].limit_unit
    } : null
    ec2_budget = var.create_service_budgets ? {
      name = aws_budgets_budget.ec2_budget[0].name
      limit = aws_budgets_budget.ec2_budget[0].limit_amount
      unit = aws_budgets_budget.ec2_budget[0].limit_unit
    } : null
    rds_budget = var.create_service_budgets ? {
      name = aws_budgets_budget.rds_budget[0].name
      limit = aws_budgets_budget.rds_budget[0].limit_amount
      unit = aws_budgets_budget.rds_budget[0].limit_unit
    } : null
    s3_budget = var.create_service_budgets ? {
      name = aws_budgets_budget.s3_budget[0].name
      limit = aws_budgets_budget.s3_budget[0].limit_amount
      unit = aws_budgets_budget.s3_budget[0].limit_unit
    } : null
  }
}

output "cloudwatch_alarms" {
  description = "CloudWatch cost alarms"
  value = {
    daily_cost_alarm = var.create_cloudwatch_alarms ? {
      name = aws_cloudwatch_metric_alarm.daily_cost_alarm[0].alarm_name
      threshold = aws_cloudwatch_metric_alarm.daily_cost_alarm[0].threshold
      arn = aws_cloudwatch_metric_alarm.daily_cost_alarm[0].arn
    } : null
    monthly_cost_alarm = var.create_cloudwatch_alarms ? {
      name = aws_cloudwatch_metric_alarm.monthly_cost_alarm[0].alarm_name
      threshold = aws_cloudwatch_metric_alarm.monthly_cost_alarm[0].threshold
      arn = aws_cloudwatch_metric_alarm.monthly_cost_alarm[0].arn
    } : null
    ec2_cost_alarm = var.create_service_alarms ? {
      name = aws_cloudwatch_metric_alarm.ec2_cost_alarm[0].alarm_name
      threshold = aws_cloudwatch_metric_alarm.ec2_cost_alarm[0].threshold
      arn = aws_cloudwatch_metric_alarm.ec2_cost_alarm[0].arn
    } : null
  }
}

output "cost_allocation" {
  description = "Cost allocation configuration"
  value = {
    cost_category = var.create_cost_allocation_tags ? {
      name = aws_ce_cost_category.cost_allocation[0].name
      arn = aws_ce_cost_category.cost_allocation[0].arn
    } : null
  }
}

output "anomaly_detection" {
  description = "Cost anomaly detection"
  value = {
    anomaly_detector = var.create_anomaly_detection ? {
      name = aws_ce_anomaly_detector.cost_anomaly[0].name
      arn = aws_ce_anomaly_detector.cost_anomaly[0].arn
    } : null
  }
}

output "cloudwatch_dashboard" {
  description = "CloudWatch cost dashboard"
  value = {
    dashboard = var.create_dashboards ? {
      name = aws_cloudwatch_dashboard.cost_dashboard[0].dashboard_name
      url = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.cost_dashboard[0].dashboard_name}"
    } : null
  }
}

output "lambda_functions" {
  description = "Lambda functions for cost automation"
  value = {
    cost_automation = var.create_lambda_functions ? {
      name = aws_lambda_function.cost_automation[0].function_name
      arn = aws_lambda_function.cost_automation[0].arn
      role_arn = aws_iam_role.cost_automation_role[0].arn
    } : null
  }
}

output "eventbridge_rules" {
  description = "EventBridge rules for cost automation"
  value = {
    daily_cost_check = var.create_eventbridge_rules ? {
      name = aws_cloudwatch_event_rule.daily_cost_check[0].name
      arn = aws_cloudwatch_event_rule.daily_cost_check[0].arn
      schedule = aws_cloudwatch_event_rule.daily_cost_check[0].schedule_expression
    } : null
    weekly_optimization = var.create_eventbridge_rules ? {
      name = aws_cloudwatch_event_rule.weekly_optimization[0].name
      arn = aws_cloudwatch_event_rule.weekly_optimization[0].arn
      schedule = aws_cloudwatch_event_rule.weekly_optimization[0].schedule_expression
    } : null
  }
}

output "s3_bucket" {
  description = "S3 bucket for cost reports"
  value = {
    bucket = var.create_s3_bucket ? {
      name = aws_s3_bucket.cost_reports[0].bucket
      arn = aws_s3_bucket.cost_reports[0].arn
      region = aws_s3_bucket.cost_reports[0].region
    } : null
  }
}

output "cost_usage_report" {
  description = "Cost and Usage Report"
  value = {
    report = var.create_cost_usage_report ? {
      name = aws_cur_report_definition.cost_usage_report[0].report_name
      s3_bucket = aws_cur_report_definition.cost_usage_report[0].s3_bucket
      s3_prefix = aws_cur_report_definition.cost_usage_report[0].s3_prefix
      format = aws_cur_report_definition.cost_usage_report[0].format
    } : null
  }
}

output "monitoring_endpoints" {
  description = "Monitoring and management endpoints"
  value = {
    cost_explorer = "https://console.aws.amazon.com/cost-management/home?region=${var.aws_region}#/dashboard"
    budgets = "https://console.aws.amazon.com/billing/home?region=${var.aws_region}#/budgets"
    cloudwatch_dashboard = var.create_dashboards ? "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.cost_dashboard[0].dashboard_name}" : ""
    cost_anomaly_detection = "https://console.aws.amazon.com/cost-management/home?region=${var.aws_region}#/anomaly-detection"
    cost_allocation_tags = "https://console.aws.amazon.com/cost-management/home?region=${var.aws_region}#/cost-categories"
  }
}

output "configuration_summary" {
  description = "Cost governance configuration summary"
  value = {
    project_name = var.project_name
    environment = var.environment
    region = var.aws_region
    monthly_budget_limit = var.monthly_budget_limit
    daily_budget_limit = var.daily_budget_limit
    alert_email = var.alert_email
    budget_email = var.budget_email
    report_email = var.report_email
    features_enabled = {
      budgets = var.create_budgets
      alarms = var.create_cloudwatch_alarms
      dashboards = var.create_dashboards
      anomaly_detection = var.create_anomaly_detection
      cost_allocation = var.create_cost_allocation_tags
      lambda_automation = var.create_lambda_functions
      eventbridge_rules = var.create_eventbridge_rules
      s3_reports = var.create_s3_bucket
      cost_usage_report = var.create_cost_usage_report
    }
  }
}

output "cost_governance_capabilities" {
  description = "Available cost governance capabilities"
  value = {
    budget_management = "Create and manage budgets with automated alerts"
    cost_monitoring = "Real-time cost monitoring with CloudWatch alarms"
    anomaly_detection = "Automated detection of unusual spending patterns"
    cost_allocation = "Tag-based cost allocation and reporting"
    optimization_recommendations = "Automated cost optimization recommendations"
    resource_rightsizing = "Identify and recommend rightsizing opportunities"
    reserved_instances = "RI purchase and utilization recommendations"
    savings_plans = "Savings Plans recommendations and management"
    unused_resource_cleanup = "Identify and clean up unused resources"
    automated_reporting = "Scheduled cost and optimization reports"
    cost_forecasting = "Predict future costs based on historical data"
    multi_account_support = "Cost governance across multiple AWS accounts"
  }
}

output "next_steps" {
  description = "Recommended next steps for cost governance"
  value = [
    "1. Configure email subscriptions for SNS topics",
    "2. Review and adjust budget thresholds based on your spending patterns",
    "3. Set up cost allocation tags on your resources",
    "4. Enable Cost and Usage Reports for detailed analysis",
    "5. Configure anomaly detection thresholds",
    "6. Review CloudWatch dashboard and customize as needed",
    "7. Set up automated cost optimization workflows",
    "8. Configure resource tagging policies",
    "9. Review and implement optimization recommendations",
    "10. Set up cross-account cost governance if needed"
  ]
}

output "cost_optimization_potential" {
  description = "Potential cost optimization areas"
  value = {
    reserved_instances = "Up to 75% savings on EC2 and RDS instances"
    savings_plans = "Up to 72% savings on compute usage"
    rightsizing = "10-30% savings by optimizing instance sizes"
    spot_instances = "Up to 90% savings for fault-tolerant workloads"
    storage_optimization = "Up to 50% savings with intelligent tiering"
    unused_resources = "Immediate savings by removing unused resources"
    auto_scaling = "10-20% savings through dynamic scaling"
    cost_allocation = "Better visibility leads to 5-15% cost reduction"
  }
}

output "monitoring_alerts" {
  description = "Monitoring and alerting configuration"
  value = {
    daily_cost_threshold = var.daily_cost_threshold
    monthly_cost_threshold = var.monthly_cost_threshold
    ec2_cost_threshold = var.ec2_cost_threshold
    alert_emails = {
      cost_alerts = var.alert_email
      budget_alerts = var.budget_email
      reports = var.report_email
    }
    notification_thresholds = var.cost_alert_thresholds
  }
}

output "automation_schedule" {
  description = "Cost automation schedule"
  value = var.automation_schedule
}

output "governance_rules" {
  description = "Active cost governance rules"
  value = var.governance_rules
}

output "optimization_targets" {
  description = "Cost optimization targets"
  value = var.optimization_targets
}

output "feature_flags" {
  description = "Feature flags status"
  value = var.feature_flags
}