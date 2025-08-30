variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "multi-vpc"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "multi-vpc-demo"
}

variable "vpc_cidr_blocks" {
  description = "CIDR blocks for each VPC"
  type        = map(string)
  default = {
    production     = "10.0.0.0/16"
    development    = "10.1.0.0/16"
    dmz            = "10.2.0.0/16"
    shared_services = "10.3.0.0/16"
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = map(list(string))
  default = {
    production     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
    development    = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
    dmz            = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
    shared_services = ["10.3.1.0/24", "10.3.2.0/24", "10.3.3.0/24"]
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = map(list(string))
  default = {
    production     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
    development    = ["10.1.11.0/24", "10.1.12.0/24", "10.1.13.0/24"]
    dmz            = ["10.2.11.0/24", "10.2.12.0/24", "10.2.13.0/24"]
    shared_services = ["10.3.11.0/24", "10.3.12.0/24", "10.3.13.0/24"]
  }
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = map(list(string))
  default = {
    production     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
    development    = ["10.1.21.0/24", "10.1.22.0/24", "10.1.23.0/24"]
    shared_services = ["10.3.21.0/24", "10.3.22.0/24", "10.3.23.0/24"]
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "RDS engine version"
  type        = string
  default     = "8.0.35"
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  default     = "changeme123!"
  sensitive   = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}
