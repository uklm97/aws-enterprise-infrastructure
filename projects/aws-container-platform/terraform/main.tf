# AWS Container & Kubernetes Platform - Main Terraform Configuration
# This file creates the core infrastructure for the container platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Configure the Kubernetes Provider
provider "kubernetes" {
  host                   = module.eks_cluster.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks_cluster.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

# Configure the Helm Provider
provider "helm" {
  kubernetes {
    host                   = module.eks_cluster.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks_cluster.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_eks_cluster_auth" "cluster" {
  name = module.eks_cluster.cluster_name
}

# Random string for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway     = true
  single_nat_gateway     = var.single_nat_gateway
  enable_vpn_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # Enable EKS cluster endpoint access
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# EKS Cluster
module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.cluster_endpoint_private_access
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      name = "main"

      instance_types = var.node_instance_types
      capacity_type  = var.node_capacity_type

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      disk_size = var.node_disk_size
      ami_type  = var.node_ami_type

      # Remote access
      remote_access = var.node_remote_access_enabled ? {
        ec2_ssh_key               = var.node_ssh_key_name
        source_security_group_ids = [aws_security_group.node_ssh.id]
      } : null

      # Launch template
      launch_template_name        = "${var.cluster_name}-launch-template"
      launch_template_description = "EKS managed node group launch template"
      launch_template_version     = "$Latest"

      # IAM role
      iam_role_name = "${var.cluster_name}-node-group-role"
      iam_role_use_name_prefix = false

      # Labels
      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      # Taints
      taints = var.node_taints

      # Tags
      tags = {
        Environment = var.environment
        NodeGroup   = "main"
      }
    }
  }

  # EKS Addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # CloudWatch Log Group
  create_cloudwatch_log_group = true
  cloudwatch_log_group_retention_in_days = var.log_retention_days

  # Cluster encryption
  cluster_encryption_config = var.cluster_encryption_enabled ? {
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  } : null

  # Cluster logging
  cluster_enabled_log_types = var.cluster_log_types

  # Tags
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# KMS Key for EKS cluster encryption
resource "aws_kms_key" "eks" {
  count = var.cluster_encryption_enabled ? 1 : 0
  
  description             = "EKS Secret Encryption Key"
  deletion_window_in_days = 7

  tags = {
    Name        = "${var.cluster_name}-eks-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "eks" {
  count = var.cluster_encryption_enabled ? 1 : 0
  
  name          = "alias/${var.cluster_name}-eks-key"
  target_key_id = aws_kms_key.eks[0].key_id
}

# Security Group for SSH access to nodes
resource "aws_security_group" "node_ssh" {
  count = var.node_remote_access_enabled ? 1 : 0
  
  name_prefix = "${var.cluster_name}-node-ssh"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.node_ssh_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.cluster_name}-node-ssh"
    Environment = var.environment
  }
}

# ECR Repositories
resource "aws_ecr_repository" "repositories" {
  for_each = toset(var.ecr_repositories)

  name                 = each.value
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = each.value
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "repositories" {
  for_each = aws_ecr_repository.repositories

  repository = each.value.name

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
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Repository Policies
resource "aws_ecr_repository_policy" "repositories" {
  for_each = aws_ecr_repository.repositories

  repository = each.value.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = [
            module.eks_cluster.node_security_group_arn,
            module.eks_cluster.cluster_iam_role_arn
          ]
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "namespaces" {
  for_each = toset(var.kubernetes_namespaces)

  metadata {
    name = each.value
    labels = {
      name        = each.value
      environment = var.environment
    }
  }
}

# Kubernetes ConfigMaps
resource "kubernetes_config_map" "config_maps" {
  for_each = var.kubernetes_config_maps

  metadata {
    name      = each.value.name
    namespace = each.value.namespace
    labels    = each.value.labels
  }

  data = each.value.data
}

# Kubernetes Secrets
resource "kubernetes_secret" "secrets" {
  for_each = var.kubernetes_secrets

  metadata {
    name      = each.value.name
    namespace = each.value.namespace
    labels    = each.value.labels
  }

  data = each.value.data
  type = each.value.type
}

# Helm Charts
resource "helm_release" "charts" {
  for_each = var.helm_charts

  name       = each.value.name
  repository = each.value.repository
  chart      = each.value.chart
  version    = each.value.version
  namespace  = each.value.namespace

  create_namespace = each.value.create_namespace
  wait             = each.value.wait
  timeout          = each.value.timeout

  values = each.value.values

  depends_on = [module.eks_cluster]
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "eks_logs" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.cluster_name}-logs"
    Environment = var.environment
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cluster_cpu_high" {
  count = var.create_alarms ? 1 : 0
  
  alarm_name          = "${var.cluster_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster CPU utilization"
  alarm_actions       = var.alarm_sns_topic_arn != null ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Name        = "${var.cluster_name}-cpu-high"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "cluster_memory_high" {
  count = var.create_alarms ? 1 : 0
  
  alarm_name          = "${var.cluster_name}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster memory utilization"
  alarm_actions       = var.alarm_sns_topic_arn != null ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Name        = "${var.cluster_name}-memory-high"
    Environment = var.environment
  }
}

# S3 Bucket for cluster backups
resource "aws_s3_bucket" "cluster_backups" {
  count = var.create_backup_bucket ? 1 : 0
  
  bucket = "${var.project_name}-cluster-backups-${random_string.suffix.result}"

  tags = {
    Name        = "${var.project_name}-cluster-backups"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "cluster_backups" {
  count = var.create_backup_bucket ? 1 : 0
  
  bucket = aws_s3_bucket.cluster_backups[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cluster_backups" {
  count = var.create_backup_bucket ? 1 : 0
  
  bucket = aws_s3_bucket.cluster_backups[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cluster_backups" {
  count = var.create_backup_bucket ? 1 : 0
  
  bucket = aws_s3_bucket.cluster_backups[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}