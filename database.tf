# RDS Parameter Groups
resource "aws_db_parameter_group" "main" {
  for_each = aws_vpc.main

  family = "mysql8.0"
  name   = "${var.project_name}-${each.key}-parameter-group"

  parameter {
    name  = "character_set_server"
    value = "utf8"
  }

  parameter {
    name  = "character_set_client"
    value = "utf8"
  }

  tags = {
    Name = "${var.project_name}-${each.key}-parameter-group"
  }
}

# RDS Option Groups
resource "aws_db_option_group" "main" {
  for_each = aws_vpc.main

  name                     = "${var.project_name}-${each.key}-option-group"
  engine_name              = "mysql"
  major_engine_version     = "8.0"

  tags = {
    Name = "${var.project_name}-${each.key}-option-group"
  }
}

# Production Database
resource "aws_db_instance" "production" {
  identifier = "${var.project_name}-production-db"

  engine         = "mysql"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "production_db"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.production_db.id]
  db_subnet_group_name   = aws_db_subnet_group.main["production"].name

  parameter_group_name = aws_db_parameter_group.main["production"].name
  option_group_name    = aws_db_option_group.main["production"].name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  multi_az               = true
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Name = "${var.project_name}-production-db"
  }
}

# Development Database
resource "aws_db_instance" "development" {
  identifier = "${var.project_name}-development-db"

  engine         = "mysql"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "development_db"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.development_db.id]
  db_subnet_group_name   = aws_db_subnet_group.main["development"].name

  parameter_group_name = aws_db_parameter_group.main["development"].name
  option_group_name    = aws_db_option_group.main["development"].name

  backup_retention_period = 3
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  multi_az               = false
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Name = "${var.project_name}-development-db"
  }
}

# Shared Services Database
resource "aws_db_instance" "shared_services" {
  identifier = "${var.project_name}-shared-db"

  engine         = "mysql"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "shared_db"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.shared_db.id]
  db_subnet_group_name   = aws_db_subnet_group.main["shared_services"].name

  parameter_group_name = aws_db_parameter_group.main["shared_services"].name
  option_group_name    = aws_db_option_group.main["shared_services"].name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  multi_az               = true
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Name = "${var.project_name}-shared-db"
  }
}

# CloudWatch Alarms for RDS
resource "aws_cloudwatch_metric_alarm" "production_db_cpu" {
  alarm_name          = "${var.project_name}-production-db-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors production RDS CPU utilization"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.production.id
  }
}

resource "aws_cloudwatch_metric_alarm" "production_db_connections" {
  alarm_name          = "${var.project_name}-production-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "100"
  alarm_description   = "This metric monitors production RDS database connections"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.production.id
  }
}

resource "aws_cloudwatch_metric_alarm" "development_db_cpu" {
  alarm_name          = "${var.project_name}-development-db-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors development RDS CPU utilization"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.development.id
  }
}

resource "aws_cloudwatch_metric_alarm" "shared_db_cpu" {
  alarm_name          = "${var.project_name}-shared-db-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors shared services RDS CPU utilization"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.shared_services.id
  }
}
