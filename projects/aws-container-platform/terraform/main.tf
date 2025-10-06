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

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.single_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Enable VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true

  # Tags for EKS
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

# EKS Cluster Module
module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.cluster_endpoint_private_access

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      name           = "main"
      instance_types = var.node_instance_types
      capacity_type  = var.node_capacity_type

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      disk_size = var.node_disk_size
      disk_type = var.node_disk_type

      # Launch template
      launch_template_name        = "${var.cluster_name}-main"
      launch_template_description = "EKS managed node group launch template"
      launch_template_version     = "$Latest"

      # IAM role
      iam_role_name = "${var.cluster_name}-main-node-role"

      # Security groups
      additional_security_group_ids = [aws_security_group.node_group.id]

      # User data
      pre_bootstrap_user_data = templatefile("${path.module}/templates/user_data.sh", {
        cluster_name = var.cluster_name
        region       = var.aws_region
      })

      # Tags
      tags = {
        Environment = var.environment
        Project     = var.project_name
        NodeGroup   = "main"
      }
    }

    # Spot instances node group
    spot = {
      name           = "spot"
      instance_types = var.spot_instance_types
      capacity_type  = "SPOT"

      min_size     = var.spot_min_size
      max_size     = var.spot_max_size
      desired_size = var.spot_desired_size

      disk_size = var.node_disk_size
      disk_type = var.node_disk_type

      # Launch template
      launch_template_name        = "${var.cluster_name}-spot"
      launch_template_description = "EKS managed node group launch template for spot instances"
      launch_template_version     = "$Latest"

      # IAM role
      iam_role_name = "${var.cluster_name}-spot-node-role"

      # Security groups
      additional_security_group_ids = [aws_security_group.node_group.id]

      # User data
      pre_bootstrap_user_data = templatefile("${path.module}/templates/user_data.sh", {
        cluster_name = var.cluster_name
        region       = var.aws_region
      })

      # Tags
      tags = {
        Environment = var.environment
        Project     = var.project_name
        NodeGroup   = "spot"
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
  create_cloudwatch_log_group            = true
  cloudwatch_log_group_retention_in_days = var.log_retention_days
  cloudwatch_log_group_kms_key_id        = aws_kms_key.eks.arn

  # Encryption
  cluster_encryption_config = {
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }

  # Tags
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# KMS Key for EKS
resource "aws_kms_key" "eks" {
  description             = "EKS Secret Encryption Key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-eks-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# Security Groups
resource "aws_security_group" "node_group" {
  name_prefix = "${var.project_name}-node-group-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  ingress {
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [module.eks_cluster.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-node-group-sg"
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
      }
    ]
  })
}

# EKS Node Group IAM Role
resource "aws_iam_role" "eks_node_group" {
  name = "${var.cluster_name}-node-group-role"

  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })

  tags = {
    Name        = "${var.cluster_name}-node-group-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_read_only" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnlyAccess"
  role       = aws_iam_role.eks_node_group.name
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "eks_cluster" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks.arn

  tags = {
    Name        = "${var.cluster_name}-cluster-logs"
    Environment = var.environment
  }
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "namespaces" {
  for_each = toset(var.kubernetes_namespaces)

  metadata {
    name = each.value
    labels = {
      name        = each.value
      environment = var.environment
      project     = var.project_name
    }
  }
}

# Helm Charts
resource "helm_release" "aws_load_balancer_controller" {
  count = var.install_aws_load_balancer_controller ? 1 : 0

  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = var.aws_load_balancer_controller_version

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  depends_on = [module.eks_cluster]
}

resource "helm_release" "cluster_autoscaler" {
  count = var.install_cluster_autoscaler ? 1 : 0

  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = var.cluster_autoscaler_version

  set {
    name  = "autoDiscovery.clusterName"
    value = var.cluster_name
  }

  set {
    name  = "awsRegion"
    value = var.aws_region
  }

  depends_on = [module.eks_cluster]
}

resource "helm_release" "metrics_server" {
  count = var.install_metrics_server ? 1 : 0

  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = var.metrics_server_version

  depends_on = [module.eks_cluster]
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cluster_cpu_utilization" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.cluster_name}-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster CPU utilization"

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Name        = "${var.cluster_name}-cpu-utilization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "cluster_memory_utilization" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.cluster_name}-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EKS cluster memory utilization"

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Name        = "${var.cluster_name}-memory-utilization"
    Environment = var.environment
  }
}