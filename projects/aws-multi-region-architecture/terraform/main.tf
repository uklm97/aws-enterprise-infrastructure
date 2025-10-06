terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "aws-multi-region-terraform-state"
    key            = "multi-region/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Primary region provider
provider "aws" {
  alias  = "primary"
  region = var.primary_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Component   = "MultiRegion"
      Region      = "primary"
    }
  }
}

# Secondary region providers
provider "aws" {
  alias  = "secondary"
  region = var.secondary_regions[0]

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Component   = "MultiRegion"
      Region      = "secondary"
    }
  }
}

provider "aws" {
  alias  = "tertiary"
  region = var.secondary_regions[1]

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Component   = "MultiRegion"
      Region      = "tertiary"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS key for encryption
resource "aws_kms_key" "multi_region_encryption" {
  provider = aws.primary
  description             = "KMS key for multi-region encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-multi-region-encryption"
    Environment = var.environment
  }
}

# S3 bucket for primary region
resource "aws_s3_bucket" "primary_bucket" {
  provider = aws.primary
  bucket   = "${var.project_name}-primary-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-primary-bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "primary_bucket" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "primary_bucket" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.multi_region_encryption.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# S3 bucket for secondary region
resource "aws_s3_bucket" "secondary_bucket" {
  provider = aws.secondary
  bucket   = "${var.project_name}-secondary-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-secondary-bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "secondary_bucket" {
  provider = aws.secondary
  bucket   = aws_s3_bucket.secondary_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secondary_bucket" {
  provider = aws.secondary
  bucket   = aws_s3_bucket.secondary_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.multi_region_encryption.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# S3 bucket for tertiary region
resource "aws_s3_bucket" "tertiary_bucket" {
  provider = aws.tertiary
  bucket   = "${var.project_name}-tertiary-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-tertiary-bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "tertiary_bucket" {
  provider = aws.tertiary
  bucket   = aws_s3_bucket.tertiary_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tertiary_bucket" {
  provider = aws.tertiary
  bucket   = aws_s3_bucket.tertiary_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.multi_region_encryption.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# S3 cross-region replication
resource "aws_s3_bucket_replication_configuration" "primary_replication" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary_bucket.id
  role     = aws_iam_role.replication_role.arn

  rule {
    id     = "replicate-to-secondary"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.secondary_bucket.arn
      storage_class = "STANDARD_IA"
    }
  }

  rule {
    id     = "replicate-to-tertiary"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.tertiary_bucket.arn
      storage_class = "STANDARD_IA"
    }
  }

  depends_on = [aws_s3_bucket_versioning.primary_bucket]
}

# IAM role for S3 replication
resource "aws_iam_role" "replication_role" {
  provider = aws.primary
  name     = "${var.project_name}-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-replication-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "replication_policy" {
  provider = aws.primary
  name     = "${var.project_name}-replication-policy"
  role     = aws_iam_role.replication_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ]
        Resource = "${aws_s3_bucket.primary_bucket.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ]
        Resource = [
          "${aws_s3_bucket.secondary_bucket.arn}/*",
          "${aws_s3_bucket.tertiary_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = aws_kms_key.multi_region_encryption.arn
      }
    ]
  })
}

# DynamoDB global tables
resource "aws_dynamodb_table" "global_table" {
  provider = aws.primary
  name     = "${var.project_name}-global-table"
  hash_key = "id"
  range_key = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  billing_mode = "PAY_PER_REQUEST"
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.multi_region_encryption.arn
  }

  replica {
    region_name = var.secondary_regions[0]
  }

  replica {
    region_name = var.secondary_regions[1]
  }

  tags = {
    Name        = "${var.project_name}-global-table"
    Environment = var.environment
  }
}

# RDS primary instance
resource "aws_db_instance" "primary_db" {
  provider = aws.primary
  identifier = "${var.project_name}-primary-db"
  engine     = var.db_engine
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type = var.db_storage_type
  storage_encrypted = true
  kms_key_id = aws_kms_key.multi_region_encryption.arn

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_primary.id]
  db_subnet_group_name   = aws_db_subnet_group.primary.name

  backup_retention_period = var.db_backup_retention_period
  backup_window          = var.db_backup_window
  maintenance_window     = var.db_maintenance_window

  skip_final_snapshot = var.db_skip_final_snapshot
  deletion_protection = var.db_deletion_protection

  tags = {
    Name        = "${var.project_name}-primary-db"
    Environment = var.environment
  }
}

# RDS read replica in secondary region
resource "aws_db_instance" "secondary_db" {
  provider = aws.secondary
  identifier = "${var.project_name}-secondary-db"
  replicate_source_db = aws_db_instance.primary_db.arn

  instance_class = var.db_instance_class
  vpc_security_group_ids = [aws_security_group.rds_secondary.id]
  db_subnet_group_name   = aws_db_subnet_group.secondary.name

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.project_name}-secondary-db"
    Environment = var.environment
  }
}

# RDS read replica in tertiary region
resource "aws_db_instance" "tertiary_db" {
  provider = aws.tertiary
  identifier = "${var.project_name}-tertiary-db"
  replicate_source_db = aws_db_instance.primary_db.arn

  instance_class = var.db_instance_class
  vpc_security_group_ids = [aws_security_group.rds_tertiary.id]
  db_subnet_group_name   = aws_db_subnet_group.tertiary.name

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.project_name}-tertiary-db"
    Environment = var.environment
  }
}

# VPC for primary region
resource "aws_vpc" "primary_vpc" {
  provider = aws.primary
  cidr_block           = var.primary_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-primary-vpc"
    Environment = var.environment
  }
}

# VPC for secondary region
resource "aws_vpc" "secondary_vpc" {
  provider = aws.secondary
  cidr_block           = var.secondary_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-secondary-vpc"
    Environment = var.environment
  }
}

# VPC for tertiary region
resource "aws_vpc" "tertiary_vpc" {
  provider = aws.tertiary
  cidr_block           = var.tertiary_vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-tertiary-vpc"
    Environment = var.environment
  }
}

# Internet Gateway for primary region
resource "aws_internet_gateway" "primary_igw" {
  provider = aws.primary
  vpc_id   = aws_vpc.primary_vpc.id

  tags = {
    Name        = "${var.project_name}-primary-igw"
    Environment = var.environment
  }
}

# Internet Gateway for secondary region
resource "aws_internet_gateway" "secondary_igw" {
  provider = aws.secondary
  vpc_id   = aws_vpc.secondary_vpc.id

  tags = {
    Name        = "${var.project_name}-secondary-igw"
    Environment = var.environment
  }
}

# Internet Gateway for tertiary region
resource "aws_internet_gateway" "tertiary_igw" {
  provider = aws.tertiary
  vpc_id   = aws_vpc.tertiary_vpc.id

  tags = {
    Name        = "${var.project_name}-tertiary-igw"
    Environment = var.environment
  }
}

# Subnets for primary region
resource "aws_subnet" "primary_public_1" {
  provider = aws.primary
  vpc_id            = aws_vpc.primary_vpc.id
  cidr_block        = var.primary_public_subnet_1_cidr
  availability_zone = "${var.primary_region}a"

  tags = {
    Name        = "${var.project_name}-primary-public-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "primary_public_2" {
  provider = aws.primary
  vpc_id            = aws_vpc.primary_vpc.id
  cidr_block        = var.primary_public_subnet_2_cidr
  availability_zone = "${var.primary_region}b"

  tags = {
    Name        = "${var.project_name}-primary-public-2"
    Environment = var.environment
  }
}

resource "aws_subnet" "primary_private_1" {
  provider = aws.primary
  vpc_id            = aws_vpc.primary_vpc.id
  cidr_block        = var.primary_private_subnet_1_cidr
  availability_zone = "${var.primary_region}a"

  tags = {
    Name        = "${var.project_name}-primary-private-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "primary_private_2" {
  provider = aws.primary
  vpc_id            = aws_vpc.primary_vpc.id
  cidr_block        = var.primary_private_subnet_2_cidr
  availability_zone = "${var.primary_region}b"

  tags = {
    Name        = "${var.project_name}-primary-private-2"
    Environment = var.environment
  }
}

# Subnets for secondary region
resource "aws_subnet" "secondary_public_1" {
  provider = aws.secondary
  vpc_id            = aws_vpc.secondary_vpc.id
  cidr_block        = var.secondary_public_subnet_1_cidr
  availability_zone = "${var.secondary_regions[0]}a"

  tags = {
    Name        = "${var.project_name}-secondary-public-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "secondary_public_2" {
  provider = aws.secondary
  vpc_id            = aws_vpc.secondary_vpc.id
  cidr_block        = var.secondary_public_subnet_2_cidr
  availability_zone = "${var.secondary_regions[0]}b"

  tags = {
    Name        = "${var.project_name}-secondary-public-2"
    Environment = var.environment
  }
}

resource "aws_subnet" "secondary_private_1" {
  provider = aws.secondary
  vpc_id            = aws_vpc.secondary_vpc.id
  cidr_block        = var.secondary_private_subnet_1_cidr
  availability_zone = "${var.secondary_regions[0]}a"

  tags = {
    Name        = "${var.project_name}-secondary-private-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "secondary_private_2" {
  provider = aws.secondary
  vpc_id            = aws_vpc.secondary_vpc.id
  cidr_block        = var.secondary_private_subnet_2_cidr
  availability_zone = "${var.secondary_regions[0]}b"

  tags = {
    Name        = "${var.project_name}-secondary-private-2"
    Environment = var.environment
  }
}

# Subnets for tertiary region
resource "aws_subnet" "tertiary_public_1" {
  provider = aws.tertiary
  vpc_id            = aws_vpc.tertiary_vpc.id
  cidr_block        = var.tertiary_public_subnet_1_cidr
  availability_zone = "${var.secondary_regions[1]}a"

  tags = {
    Name        = "${var.project_name}-tertiary-public-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "tertiary_public_2" {
  provider = aws.tertiary
  vpc_id            = aws_vpc.tertiary_vpc.id
  cidr_block        = var.tertiary_public_subnet_2_cidr
  availability_zone = "${var.secondary_regions[1]}b"

  tags = {
    Name        = "${var.project_name}-tertiary-public-2"
    Environment = var.environment
  }
}

resource "aws_subnet" "tertiary_private_1" {
  provider = aws.tertiary
  vpc_id            = aws_vpc.tertiary_vpc.id
  cidr_block        = var.tertiary_private_subnet_1_cidr
  availability_zone = "${var.secondary_regions[1]}a"

  tags = {
    Name        = "${var.project_name}-tertiary-private-1"
    Environment = var.environment
  }
}

resource "aws_subnet" "tertiary_private_2" {
  provider = aws.tertiary
  vpc_id            = aws_vpc.tertiary_vpc.id
  cidr_block        = var.tertiary_private_subnet_2_cidr
  availability_zone = "${var.secondary_regions[1]}b"

  tags = {
    Name        = "${var.project_name}-tertiary-private-2"
    Environment = var.environment
  }
}

# Route tables for primary region
resource "aws_route_table" "primary_public" {
  provider = aws.primary
  vpc_id = aws_vpc.primary_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.primary_igw.id
  }

  tags = {
    Name        = "${var.project_name}-primary-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "primary_private" {
  provider = aws.primary
  vpc_id = aws_vpc.primary_vpc.id

  tags = {
    Name        = "${var.project_name}-primary-private-rt"
    Environment = var.environment
  }
}

# Route table associations for primary region
resource "aws_route_table_association" "primary_public_1" {
  provider = aws.primary
  subnet_id      = aws_subnet.primary_public_1.id
  route_table_id = aws_route_table.primary_public.id
}

resource "aws_route_table_association" "primary_public_2" {
  provider = aws.primary
  subnet_id      = aws_subnet.primary_public_2.id
  route_table_id = aws_route_table.primary_public.id
}

resource "aws_route_table_association" "primary_private_1" {
  provider = aws.primary
  subnet_id      = aws_subnet.primary_private_1.id
  route_table_id = aws_route_table.primary_private.id
}

resource "aws_route_table_association" "primary_private_2" {
  provider = aws.primary
  subnet_id      = aws_subnet.primary_private_2.id
  route_table_id = aws_route_table.primary_private.id
}

# Route tables for secondary region
resource "aws_route_table" "secondary_public" {
  provider = aws.secondary
  vpc_id = aws_vpc.secondary_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.secondary_igw.id
  }

  tags = {
    Name        = "${var.project_name}-secondary-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "secondary_private" {
  provider = aws.secondary
  vpc_id = aws_vpc.secondary_vpc.id

  tags = {
    Name        = "${var.project_name}-secondary-private-rt"
    Environment = var.environment
  }
}

# Route table associations for secondary region
resource "aws_route_table_association" "secondary_public_1" {
  provider = aws.secondary
  subnet_id      = aws_subnet.secondary_public_1.id
  route_table_id = aws_route_table.secondary_public.id
}

resource "aws_route_table_association" "secondary_public_2" {
  provider = aws.secondary
  subnet_id      = aws_subnet.secondary_public_2.id
  route_table_id = aws_route_table.secondary_public.id
}

resource "aws_route_table_association" "secondary_private_1" {
  provider = aws.secondary
  subnet_id      = aws_subnet.secondary_private_1.id
  route_table_id = aws_route_table.secondary_private.id
}

resource "aws_route_table_association" "secondary_private_2" {
  provider = aws.secondary
  subnet_id      = aws_subnet.secondary_private_2.id
  route_table_id = aws_route_table.secondary_private.id
}

# Route tables for tertiary region
resource "aws_route_table" "tertiary_public" {
  provider = aws.tertiary
  vpc_id = aws_vpc.tertiary_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.tertiary_igw.id
  }

  tags = {
    Name        = "${var.project_name}-tertiary-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "tertiary_private" {
  provider = aws.tertiary
  vpc_id = aws_vpc.tertiary_vpc.id

  tags = {
    Name        = "${var.project_name}-tertiary-private-rt"
    Environment = var.environment
  }
}

# Route table associations for tertiary region
resource "aws_route_table_association" "tertiary_public_1" {
  provider = aws.tertiary
  subnet_id      = aws_subnet.tertiary_public_1.id
  route_table_id = aws_route_table.tertiary_public.id
}

resource "aws_route_table_association" "tertiary_public_2" {
  provider = aws.tertiary
  subnet_id      = aws_subnet.tertiary_public_2.id
  route_table_id = aws_route_table.tertiary_public.id
}

resource "aws_route_table_association" "tertiary_private_1" {
  provider = aws.tertiary
  subnet_id      = aws_subnet.tertiary_private_1.id
  route_table_id = aws_route_table.tertiary_private.id
}

resource "aws_route_table_association" "tertiary_private_2" {
  provider = aws.tertiary
  subnet_id      = aws_subnet.tertiary_private_2.id
  route_table_id = aws_route_table.tertiary_private.id
}

# Security groups for primary region
resource "aws_security_group" "rds_primary" {
  provider = aws.primary
  name        = "${var.project_name}-rds-primary"
  description = "Security group for primary RDS instance"
  vpc_id      = aws_vpc.primary_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.primary_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-rds-primary"
    Environment = var.environment
  }
}

# Security groups for secondary region
resource "aws_security_group" "rds_secondary" {
  provider = aws.secondary
  name        = "${var.project_name}-rds-secondary"
  description = "Security group for secondary RDS instance"
  vpc_id      = aws_vpc.secondary_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.secondary_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-rds-secondary"
    Environment = var.environment
  }
}

# Security groups for tertiary region
resource "aws_security_group" "rds_tertiary" {
  provider = aws.tertiary
  name        = "${var.project_name}-rds-tertiary"
  description = "Security group for tertiary RDS instance"
  vpc_id      = aws_vpc.tertiary_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.tertiary_vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-rds-tertiary"
    Environment = var.environment
  }
}

# DB subnet groups
resource "aws_db_subnet_group" "primary" {
  provider = aws.primary
  name       = "${var.project_name}-primary-db-subnet-group"
  subnet_ids = [aws_subnet.primary_private_1.id, aws_subnet.primary_private_2.id]

  tags = {
    Name        = "${var.project_name}-primary-db-subnet-group"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "secondary" {
  provider = aws.secondary
  name       = "${var.project_name}-secondary-db-subnet-group"
  subnet_ids = [aws_subnet.secondary_private_1.id, aws_subnet.secondary_private_2.id]

  tags = {
    Name        = "${var.project_name}-secondary-db-subnet-group"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "tertiary" {
  provider = aws.tertiary
  name       = "${var.project_name}-tertiary-db-subnet-group"
  subnet_ids = [aws_subnet.tertiary_private_1.id, aws_subnet.tertiary_private_2.id]

  tags = {
    Name        = "${var.project_name}-tertiary-db-subnet-group"
    Environment = var.environment
  }
}

# Random string for bucket suffix
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "global_distribution" {
  provider = aws.primary
  origin {
    domain_name = aws_s3_bucket.primary_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.primary_bucket.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.primary_oai.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Global distribution for multi-region architecture"
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.primary_bucket.bucket}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_All"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name        = "${var.project_name}-global-distribution"
    Environment = var.environment
  }
}

# CloudFront origin access identity
resource "aws_cloudfront_origin_access_identity" "primary_oai" {
  provider = aws.primary
  comment = "OAI for primary S3 bucket"
}

# S3 bucket policy for CloudFront
resource "aws_s3_bucket_policy" "primary_bucket_policy" {
  provider = aws.primary
  bucket = aws_s3_bucket.primary_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${aws_cloudfront_origin_access_identity.primary_oai.id}"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.primary_bucket.arn}/*"
      }
    ]
  })
}

# Route53 hosted zone
resource "aws_route53_zone" "main" {
  provider = aws.primary
  name = var.domain_name

  tags = {
    Name        = "${var.project_name}-hosted-zone"
    Environment = var.environment
  }
}

# Route53 record for CloudFront
resource "aws_route53_record" "main" {
  provider = aws.primary
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.global_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.global_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 health checks
resource "aws_route53_health_check" "primary" {
  provider = aws.primary
  fqdn              = var.domain_name
  port              = 80
  type              = "HTTP"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"

  tags = {
    Name        = "${var.project_name}-health-check-primary"
    Environment = var.environment
  }
}

resource "aws_route53_health_check" "secondary" {
  provider = aws.primary
  fqdn              = var.domain_name
  port              = 80
  type              = "HTTP"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"

  tags = {
    Name        = "${var.project_name}-health-check-secondary"
    Environment = var.environment
  }
}

# Route53 failover records
resource "aws_route53_record" "primary" {
  provider = aws.primary
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  failover_routing_policy {
    type = "PRIMARY"
  }

  health_check_id = aws_route53_health_check.primary.id
  set_identifier  = "primary"

  alias {
    name                   = aws_cloudfront_distribution.global_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.global_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "secondary" {
  provider = aws.primary
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  failover_routing_policy {
    type = "SECONDARY"
  }

  health_check_id = aws_route53_health_check.secondary.id
  set_identifier  = "secondary"

  alias {
    name                   = aws_cloudfront_distribution.global_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.global_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}