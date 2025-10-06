# AWS Data & Analytics Platform - Main Terraform Configuration
# This file creates the core infrastructure for the data analytics platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random string for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Data Lake Bucket
resource "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_bucket_name
  
  tags = {
    Name        = var.data_lake_bucket_name
    Environment = var.environment
    Purpose     = "data-lake"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "data_lake_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Glue Data Catalog
resource "aws_glue_catalog_database" "data_lake" {
  name = "${var.project_name}-catalog"
  
  tags = {
    Name        = "${var.project_name}-catalog"
    Environment = var.environment
  }
}

# Glue Crawler Role
resource "aws_iam_role" "glue_crawler_role" {
  name = "${var.project_name}-glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-glue-crawler-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "glue_service_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
  role       = aws_iam_role.glue_crawler_role.name
}

resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "${var.project_name}-glue-s3-policy"
  role = aws_iam_role.glue_crawler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# Glue Crawler
resource "aws_glue_crawler" "data_lake" {
  name          = "${var.project_name}-crawler"
  database_name = aws_glue_catalog_database.data_lake.name
  role          = aws_iam_role.glue_crawler_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/processed/"
  }

  schedule = "cron(0 2 * * ? *)"

  tags = {
    Name        = "${var.project_name}-crawler"
    Environment = var.environment
  }
}

# Redshift Cluster
resource "aws_redshift_cluster" "main" {
  cluster_identifier        = var.redshift_cluster_identifier
  database_name            = var.redshift_database_name
  master_username          = var.redshift_master_username
  master_password          = var.redshift_master_password
  node_type                = var.redshift_node_type
  cluster_type             = var.redshift_cluster_type
  number_of_nodes          = var.redshift_number_of_nodes
  skip_final_snapshot      = var.redshift_skip_final_snapshot
  automated_snapshot_retention_period = var.redshift_snapshot_retention_period
  encrypted                = true
  publicly_accessible      = false

  logging {
    enable        = true
    bucket_name   = aws_s3_bucket.data_lake.bucket
    s3_key_prefix = "redshift-logs/"
  }

  tags = {
    Name        = var.redshift_cluster_identifier
    Environment = var.environment
  }
}

# Redshift Subnet Group
resource "aws_redshift_subnet_group" "main" {
  name       = "${var.project_name}-redshift-subnet-group"
  subnet_ids = var.redshift_subnet_ids

  tags = {
    Name        = "${var.project_name}-redshift-subnet-group"
    Environment = var.environment
  }
}

# Redshift Security Group
resource "aws_security_group" "redshift" {
  name_prefix = "${var.project_name}-redshift-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = var.redshift_allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-redshift-sg"
    Environment = var.environment
  }
}

# Kinesis Data Stream
resource "aws_kinesis_stream" "main" {
  name             = "${var.project_name}-data-stream"
  shard_count      = var.kinesis_shard_count
  retention_period = var.kinesis_retention_period

  shard_level_metrics = [
    "IncomingRecords",
    "OutgoingRecords",
  ]

  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis.arn

  tags = {
    Name        = "${var.project_name}-data-stream"
    Environment = var.environment
  }
}

# Kinesis Data Firehose
resource "aws_kinesis_firehose_delivery_stream" "main" {
  name        = "${var.project_name}-firehose"
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.main.arn
    role_arn          = aws_iam_role.firehose_role.arn
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.data_lake.arn
    prefix     = "raw/kinesis/"

    buffering_size     = 64
    buffering_interval = 60
    compression_format = "GZIP"

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose.name
      log_stream_name = "S3Delivery"
    }
  }

  tags = {
    Name        = "${var.project_name}-firehose"
    Environment = var.environment
  }
}

# Kinesis Firehose IAM Role
resource "aws_iam_role" "firehose_role" {
  name = "${var.project_name}-firehose-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-firehose-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "firehose_s3_policy" {
  name = "${var.project_name}-firehose-s3-policy"
  role = aws_iam_role.firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "firehose_kinesis_policy" {
  name = "${var.project_name}-firehose-kinesis-policy"
  role = aws_iam_role.firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards"
        ]
        Resource = aws_kinesis_stream.main.arn
      }
    ]
  })
}

# SageMaker Notebook Instance
resource "aws_sagemaker_notebook_instance" "main" {
  count = var.create_sagemaker_notebook ? 1 : 0

  name          = "${var.project_name}-notebook"
  instance_type = var.sagemaker_instance_type
  role_arn      = aws_iam_role.sagemaker_role.arn

  volume_size = var.sagemaker_volume_size

  tags = {
    Name        = "${var.project_name}-notebook"
    Environment = var.environment
  }
}

# SageMaker IAM Role
resource "aws_iam_role" "sagemaker_role" {
  name = "${var.project_name}-sagemaker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-sagemaker-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
  role       = aws_iam_role.sagemaker_role.name
}

resource "aws_iam_role_policy" "sagemaker_s3_policy" {
  name = "${var.project_name}-sagemaker-s3-policy"
  role = aws_iam_role.sagemaker_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# KMS Key for Kinesis
resource "aws_kms_key" "kinesis" {
  description             = "KMS key for Kinesis Data Stream"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-kinesis-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "kinesis" {
  name          = "alias/${var.project_name}-kinesis"
  target_key_id = aws_kms_key.kinesis.key_id
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "data_analytics" {
  name              = "/aws/data-analytics/${var.project_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.kinesis.arn

  tags = {
    Name        = "${var.project_name}-data-analytics-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "firehose" {
  name              = "/aws/kinesisfirehose/${var.project_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-firehose-logs"
    Environment = var.environment
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "kinesis_incoming_records" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-kinesis-incoming-records"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "IncomingRecords"
  namespace           = "AWS/Kinesis"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors kinesis incoming records"

  dimensions = {
    StreamName = aws_kinesis_stream.main.name
  }

  tags = {
    Name        = "${var.project_name}-kinesis-incoming-records"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "redshift_cpu_utilization" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-redshift-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/Redshift"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors redshift cpu utilization"

  dimensions = {
    ClusterIdentifier = aws_redshift_cluster.main.cluster_identifier
  }

  tags = {
    Name        = "${var.project_name}-redshift-cpu-utilization"
    Environment = var.environment
  }
}