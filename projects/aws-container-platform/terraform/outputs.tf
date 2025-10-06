# AWS Container & Kubernetes Platform - Outputs
# This file defines all the output values for the Terraform configuration

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

# EKS Cluster Outputs
output "cluster_id" {
  description = "The name/id of the EKS cluster"
  value       = module.eks_cluster.cluster_id
}

output "cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster"
  value       = module.eks_cluster.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks_cluster.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks_cluster.cluster_security_group_id
}

output "cluster_primary_security_group_id" {
  description = "The cluster primary security group ID created by EKS"
  value       = module.eks_cluster.cluster_primary_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks_cluster.cluster_certificate_authority_data
}

output "cluster_platform_version" {
  description = "Platform version for the EKS cluster"
  value       = module.eks_cluster.cluster_platform_version
}

output "cluster_status" {
  description = "Status of the EKS cluster"
  value       = module.eks_cluster.cluster_status
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks_cluster.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks_cluster.cluster_iam_role_arn
}

# EKS Node Groups Outputs
output "eks_managed_node_groups" {
  description = "Map of attribute maps for all EKS managed node groups created"
  value       = module.eks_cluster.eks_managed_node_groups
}

output "eks_managed_node_groups_autoscaling_group_names" {
  description = "List of the autoscaling group names created by EKS managed node groups"
  value       = module.eks_cluster.eks_managed_node_groups_autoscaling_group_names
}

# EKS Addons Outputs
output "cluster_addons" {
  description = "Map of attribute maps for all EKS cluster addons created"
  value       = module.eks_cluster.cluster_addons
}

# ECR Outputs
output "ecr_repository_urls" {
  description = "Map of ECR repository URLs"
  value = {
    for k, v in aws_ecr_repository.repositories : k => v.repository_url
  }
}

output "ecr_repository_arns" {
  description = "Map of ECR repository ARNs"
  value = {
    for k, v in aws_ecr_repository.repositories : k => v.arn
  }
}

# KMS Outputs
output "kms_key_id" {
  description = "The globally unique identifier for the key"
  value       = aws_kms_key.eks.key_id
}

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the key"
  value       = aws_kms_key.eks.arn
}

output "kms_alias_name" {
  description = "The display name of the alias"
  value       = aws_kms_alias.eks.name
}

# CloudWatch Logs Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.eks_cluster.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.eks_cluster.arn
}

# Kubernetes Namespaces Outputs
output "kubernetes_namespaces" {
  description = "List of created Kubernetes namespaces"
  value       = [for k, v in kubernetes_namespace.namespaces : v.metadata[0].name]
}

# Helm Releases Outputs
output "aws_load_balancer_controller_status" {
  description = "Status of the AWS Load Balancer Controller Helm release"
  value       = var.install_aws_load_balancer_controller ? helm_release.aws_load_balancer_controller[0].status : null
}

output "cluster_autoscaler_status" {
  description = "Status of the Cluster Autoscaler Helm release"
  value       = var.install_cluster_autoscaler ? helm_release.cluster_autoscaler[0].status : null
}

output "metrics_server_status" {
  description = "Status of the Metrics Server Helm release"
  value       = var.install_metrics_server ? helm_release.metrics_server[0].status : null
}

# CloudWatch Alarms Outputs
output "cpu_utilization_alarm_arn" {
  description = "ARN of the CPU utilization CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_cpu_utilization[0].arn : null
}

output "memory_utilization_alarm_arn" {
  description = "ARN of the memory utilization CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_memory_utilization[0].arn : null
}

# General Information
output "aws_region" {
  description = "AWS region where resources are created"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "project_name" {
  description = "Name of the project"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# kubectl Configuration
output "kubectl_config" {
  description = "kubectl configuration commands"
  value = {
    update_kubeconfig = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
    cluster_name      = var.cluster_name
    cluster_endpoint  = module.eks_cluster.cluster_endpoint
  }
}