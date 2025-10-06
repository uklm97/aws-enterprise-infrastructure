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

output "nat_gateway_ids" {
  description = "List of IDs of the NAT Gateways"
  value       = module.vpc.natgw_ids
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

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks_cluster.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks_cluster.cluster_iam_role_arn
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

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = module.eks_cluster.cluster_version
}

# Node Group Outputs
output "node_groups" {
  description = "Map of attribute maps for all EKS node groups"
  value       = module.eks_cluster.eks_managed_node_groups
}

output "node_security_group_id" {
  description = "ID of the node shared security group"
  value       = module.eks_cluster.node_security_group_id
}

output "node_security_group_arn" {
  description = "Amazon Resource Name (ARN) of the node shared security group"
  value       = module.eks_cluster.node_security_group_arn
}

# ECR Outputs
output "ecr_repository_urls" {
  description = "Map of ECR repository URLs"
  value       = { for k, v in aws_ecr_repository.repositories : k => v.repository_url }
}

output "ecr_repository_arns" {
  description = "Map of ECR repository ARNs"
  value       = { for k, v in aws_ecr_repository.repositories : k => v.arn }
}

# KMS Outputs
output "kms_key_id" {
  description = "The globally unique identifier for the key"
  value       = var.cluster_encryption_enabled ? aws_kms_key.eks[0].key_id : null
}

output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the key"
  value       = var.cluster_encryption_enabled ? aws_kms_key.eks[0].arn : null
}

output "kms_alias_name" {
  description = "The display name of the alias"
  value       = var.cluster_encryption_enabled ? aws_kms_alias.eks[0].name : null
}

# CloudWatch Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.eks_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.eks_logs.arn
}

# CloudWatch Alarms
output "cpu_high_alarm_name" {
  description = "Name of the CPU high CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_cpu_high[0].alarm_name : null
}

output "cpu_high_alarm_arn" {
  description = "ARN of the CPU high CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_cpu_high[0].arn : null
}

output "memory_high_alarm_name" {
  description = "Name of the memory high CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_memory_high[0].alarm_name : null
}

output "memory_high_alarm_arn" {
  description = "ARN of the memory high CloudWatch alarm"
  value       = var.create_alarms ? aws_cloudwatch_metric_alarm.cluster_memory_high[0].arn : null
}

# S3 Backup Outputs
output "backup_bucket_name" {
  description = "Name of the S3 bucket for cluster backups"
  value       = var.create_backup_bucket ? aws_s3_bucket.cluster_backups[0].bucket : null
}

output "backup_bucket_arn" {
  description = "ARN of the S3 bucket for cluster backups"
  value       = var.create_backup_bucket ? aws_s3_bucket.cluster_backups[0].arn : null
}

# Kubernetes Outputs
output "kubernetes_namespaces" {
  description = "List of created Kubernetes namespaces"
  value       = [for ns in kubernetes_namespace.namespaces : ns.metadata[0].name]
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
  value = <<-EOT
    # Update kubeconfig
    aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks_cluster.cluster_name}
    
    # Verify cluster access
    kubectl get nodes
    kubectl get pods --all-namespaces
  EOT
}

# Helm Configuration
output "helm_config" {
  description = "Helm configuration commands"
  value = <<-EOT
    # Add Helm repositories
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
    helm repo update
    
    # List installed charts
    helm list --all-namespaces
  EOT
}