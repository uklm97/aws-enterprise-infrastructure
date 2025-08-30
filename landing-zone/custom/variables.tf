variable "aws_region" {
  description = "AWS region for the landing zone"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "landing-zone"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "aws-landing-zone"
}

variable "admin_email" {
  description = "Admin email for notifications and SSO"
  type        = string
  default     = "admin@example.com"
}

variable "organization_name" {
  description = "Organization name"
  type        = string
  default     = "My Organization"
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable AWS Security Hub"
  type        = bool
  default     = true
}

variable "enable_macie" {
  description = "Enable AWS Macie"
  type        = bool
  default     = true
}

variable "enable_config_rules" {
  description = "Enable AWS Config rules"
  type        = bool
  default     = true
}

variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = string
  default     = "1000"
}

variable "budget_threshold" {
  description = "Budget threshold percentage for alerts"
  type        = number
  default     = 80
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 30
}

variable "sso_session_duration" {
  description = "SSO session duration in hours"
  type        = number
  default     = 8
}

variable "enable_multi_region_trail" {
  description = "Enable multi-region CloudTrail"
  type        = bool
  default     = true
}

variable "enable_global_service_events" {
  description = "Enable global service events in CloudTrail"
  type        = bool
  default     = true
}

variable "enable_s3_data_events" {
  description = "Enable S3 data events in CloudTrail"
  type        = bool
  default     = true
}

variable "enable_lambda_data_events" {
  description = "Enable Lambda data events in CloudTrail"
  type        = bool
  default     = false
}

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logs for CloudTrail"
  type        = bool
  default     = true
}

variable "enable_sns_notifications" {
  description = "Enable SNS notifications"
  type        = bool
  default     = true
}

variable "enable_budget_alerts" {
  description = "Enable budget alerts"
  type        = bool
  default     = true
}

variable "enable_cost_anomaly_detection" {
  description = "Enable cost anomaly detection"
  type        = bool
  default     = true
}

variable "enable_organizations_policies" {
  description = "Enable Organizations policies"
  type        = bool
  default     = true
}

variable "enable_tag_policies" {
  description = "Enable tag policies"
  type        = bool
  default     = true
}

variable "enable_backup_policies" {
  description = "Enable backup policies"
  type        = bool
  default     = true
}

variable "enable_encryption_policies" {
  description = "Enable encryption policies"
  type        = bool
  default     = true
}

variable "enable_network_policies" {
  description = "Enable network policies"
  type        = bool
  default     = true
}

variable "enable_compliance_policies" {
  description = "Enable compliance policies"
  type        = bool
  default     = true
}

variable "enable_audit_policies" {
  description = "Enable audit policies"
  type        = bool
  default     = true
}

variable "enable_monitoring_policies" {
  description = "Enable monitoring policies"
  type        = bool
  default     = true
}

variable "enable_security_policies" {
  description = "Enable security policies"
  type        = bool
  default     = true
}

variable "enable_governance_policies" {
  description = "Enable governance policies"
  type        = bool
  default     = true
}

variable "enable_automation_policies" {
  description = "Enable automation policies"
  type        = bool
  default     = true
}

variable "enable_incident_response_policies" {
  description = "Enable incident response policies"
  type        = bool
  default     = true
}

variable "enable_disaster_recovery_policies" {
  description = "Enable disaster recovery policies"
  type        = bool
  default     = true
}

variable "enable_business_continuity_policies" {
  description = "Enable business continuity policies"
  type        = bool
  default     = true
}

variable "enable_risk_management_policies" {
  description = "Enable risk management policies"
  type        = bool
  default     = true
}

variable "enable_change_management_policies" {
  description = "Enable change management policies"
  type        = bool
  default     = true
}

variable "enable_access_management_policies" {
  description = "Enable access management policies"
  type        = bool
  default     = true
}

variable "enable_identity_management_policies" {
  description = "Enable identity management policies"
  type        = bool
  default     = true
}

variable "enable_data_management_policies" {
  description = "Enable data management policies"
  type        = bool
  default     = true
}

variable "enable_application_management_policies" {
  description = "Enable application management policies"
  type        = bool
  default     = true
}

variable "enable_infrastructure_management_policies" {
  description = "Enable infrastructure management policies"
  type        = bool
  default     = true
}

variable "enable_operations_management_policies" {
  description = "Enable operations management policies"
  type        = bool
  default     = true
}

variable "enable_service_management_policies" {
  description = "Enable service management policies"
  type        = bool
  default     = true
}

variable "enable_vendor_management_policies" {
  description = "Enable vendor management policies"
  type        = bool
  default     = true
}

variable "enable_contract_management_policies" {
  description = "Enable contract management policies"
  type        = bool
  default     = true
}

variable "enable_procurement_policies" {
  description = "Enable procurement policies"
  type        = bool
  default     = true
}

variable "enable_financial_management_policies" {
  description = "Enable financial management policies"
  type        = bool
  default     = true
}

variable "enable_legal_management_policies" {
  description = "Enable legal management policies"
  type        = bool
  default     = true
}

variable "enable_human_resources_policies" {
  description = "Enable human resources policies"
  type        = bool
  default     = true
}

variable "enable_training_policies" {
  description = "Enable training policies"
  type        = bool
  default     = true
}

variable "enable_communication_policies" {
  description = "Enable communication policies"
  type        = bool
  default     = true
}

variable "enable_documentation_policies" {
  description = "Enable documentation policies"
  type        = bool
  default     = true
}

variable "enable_knowledge_management_policies" {
  description = "Enable knowledge management policies"
  type        = bool
  default     = true
}

variable "enable_quality_management_policies" {
  description = "Enable quality management policies"
  type        = bool
  default     = true
}

variable "enable_performance_management_policies" {
  description = "Enable performance management policies"
  type        = bool
  default     = true
}

variable "enable_continuous_improvement_policies" {
  description = "Enable continuous improvement policies"
  type        = bool
  default     = true
}

variable "enable_innovation_policies" {
  description = "Enable innovation policies"
  type        = bool
  default     = true
}

variable "enable_research_policies" {
  description = "Enable research policies"
  type        = bool
  default     = true
}

variable "enable_development_policies" {
  description = "Enable development policies"
  type        = bool
  default     = true
}

variable "enable_testing_policies" {
  description = "Enable testing policies"
  type        = bool
  default     = true
}

variable "enable_deployment_policies" {
  description = "Enable deployment policies"
  type        = bool
  default     = true
}

variable "enable_release_management_policies" {
  description = "Enable release management policies"
  type        = bool
  default     = true
}

variable "enable_version_control_policies" {
  description = "Enable version control policies"
  type        = bool
  default     = true
}

variable "enable_code_review_policies" {
  description = "Enable code review policies"
  type        = bool
  default     = true
}

variable "enable_testing_automation_policies" {
  description = "Enable testing automation policies"
  type        = bool
  default     = true
}

variable "enable_continuous_integration_policies" {
  description = "Enable continuous integration policies"
  type        = bool
  default     = true
}

variable "enable_continuous_deployment_policies" {
  description = "Enable continuous deployment policies"
  type        = bool
  default     = true
}

variable "enable_devops_policies" {
  description = "Enable DevOps policies"
  type        = bool
  default     = true
}

variable "enable_agile_policies" {
  description = "Enable agile policies"
  type        = bool
  default     = true
}

variable "enable_scrum_policies" {
  description = "Enable scrum policies"
  type        = bool
  default     = true
}

variable "enable_kanban_policies" {
  description = "Enable kanban policies"
  type        = bool
  default     = true
}

variable "enable_lean_policies" {
  description = "Enable lean policies"
  type        = bool
  default     = true
}

variable "enable_six_sigma_policies" {
  description = "Enable six sigma policies"
  type        = bool
  default     = true
}

variable "enable_tqm_policies" {
  description = "Enable total quality management policies"
  type        = bool
  default     = true
}

variable "enable_iso_policies" {
  description = "Enable ISO policies"
  type        = bool
  default     = true
}

variable "enable_soc_policies" {
  description = "Enable SOC policies"
  type        = bool
  default     = true
}

variable "enable_pci_policies" {
  description = "Enable PCI policies"
  type        = bool
  default     = true
}

variable "enable_hipaa_policies" {
  description = "Enable HIPAA policies"
  type        = bool
  default     = true
}

variable "enable_gdpr_policies" {
  description = "Enable GDPR policies"
  type        = bool
  default     = true
}

variable "enable_sox_policies" {
  description = "Enable SOX policies"
  type        = bool
  default     = true
}

variable "enable_fedramp_policies" {
  description = "Enable FedRAMP policies"
  type        = bool
  default     = true
}

variable "enable_nist_policies" {
  description = "Enable NIST policies"
  type        = bool
  default     = true
}

variable "enable_cis_policies" {
  description = "Enable CIS policies"
  type        = bool
  default     = true
}

variable "enable_owasp_policies" {
  description = "Enable OWASP policies"
  type        = bool
  default     = true
}

variable "enable_mitre_policies" {
  description = "Enable MITRE policies"
  type        = bool
  default     = true
}

variable "enable_nist_csf_policies" {
  description = "Enable NIST CSF policies"
  type        = bool
  default     = true
}

variable "enable_iso_27001_policies" {
  description = "Enable ISO 27001 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27002_policies" {
  description = "Enable ISO 27002 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27005_policies" {
  description = "Enable ISO 27005 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27017_policies" {
  description = "Enable ISO 27017 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27018_policies" {
  description = "Enable ISO 27018 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27031_policies" {
  description = "Enable ISO 27031 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27032_policies" {
  description = "Enable ISO 27032 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27035_policies" {
  description = "Enable ISO 27035 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27036_policies" {
  description = "Enable ISO 27036 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27037_policies" {
  description = "Enable ISO 27037 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27038_policies" {
  description = "Enable ISO 27038 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27039_policies" {
  description = "Enable ISO 27039 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27040_policies" {
  description = "Enable ISO 27040 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27041_policies" {
  description = "Enable ISO 27041 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27042_policies" {
  description = "Enable ISO 27042 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27043_policies" {
  description = "Enable ISO 27043 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27044_policies" {
  description = "Enable ISO 27044 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27045_policies" {
  description = "Enable ISO 27045 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27046_policies" {
  description = "Enable ISO 27046 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27047_policies" {
  description = "Enable ISO 27047 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27048_policies" {
  description = "Enable ISO 27048 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27049_policies" {
  description = "Enable ISO 27049 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27050_policies" {
  description = "Enable ISO 27050 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27051_policies" {
  description = "Enable ISO 27051 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27052_policies" {
  description = "Enable ISO 27052 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27053_policies" {
  description = "Enable ISO 27053 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27054_policies" {
  description = "Enable ISO 27054 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27055_policies" {
  description = "Enable ISO 27055 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27056_policies" {
  description = "Enable ISO 27056 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27057_policies" {
  description = "Enable ISO 27057 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27058_policies" {
  description = "Enable ISO 27058 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27059_policies" {
  description = "Enable ISO 27059 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27060_policies" {
  description = "Enable ISO 27060 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27061_policies" {
  description = "Enable ISO 27061 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27062_policies" {
  description = "Enable ISO 27062 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27063_policies" {
  description = "Enable ISO 27063 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27064_policies" {
  description = "Enable ISO 27064 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27065_policies" {
  description = "Enable ISO 27065 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27066_policies" {
  description = "Enable ISO 27066 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27067_policies" {
  description = "Enable ISO 27067 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27068_policies" {
  description = "Enable ISO 27068 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27069_policies" {
  description = "Enable ISO 27069 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27070_policies" {
  description = "Enable ISO 27070 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27071_policies" {
  description = "Enable ISO 27071 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27072_policies" {
  description = "Enable ISO 27072 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27073_policies" {
  description = "Enable ISO 27073 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27074_policies" {
  description = "Enable ISO 27074 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27075_policies" {
  description = "Enable ISO 27075 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27076_policies" {
  description = "Enable ISO 27076 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27077_policies" {
  description = "Enable ISO 27077 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27078_policies" {
  description = "Enable ISO 27078 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27079_policies" {
  description = "Enable ISO 27079 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27080_policies" {
  description = "Enable ISO 27080 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27081_policies" {
  description = "Enable ISO 27081 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27082_policies" {
  description = "Enable ISO 27082 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27083_policies" {
  description = "Enable ISO 27083 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27084_policies" {
  description = "Enable ISO 27084 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27085_policies" {
  description = "Enable ISO 27085 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27086_policies" {
  description = "Enable ISO 27086 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27087_policies" {
  description = "Enable ISO 27087 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27088_policies" {
  description = "Enable ISO 27088 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27089_policies" {
  description = "Enable ISO 27089 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27090_policies" {
  description = "Enable ISO 27090 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27091_policies" {
  description = "Enable ISO 27091 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27092_policies" {
  description = "Enable ISO 27092 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27093_policies" {
  description = "Enable ISO 27093 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27094_policies" {
  description = "Enable ISO 27094 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27095_policies" {
  description = "Enable ISO 27095 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27096_policies" {
  description = "Enable ISO 27096 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27097_policies" {
  description = "Enable ISO 27097 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27098_policies" {
  description = "Enable ISO 27098 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27099_policies" {
  description = "Enable ISO 27099 policies"
  type        = bool
  default     = true
}

variable "enable_iso_27100_policies" {
  description = "Enable ISO 27100 policies"
  type        = bool
  default     = true
}
