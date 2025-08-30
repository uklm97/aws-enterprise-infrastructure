# VPC Information
output "vpc_ids" {
  description = "IDs of the created VPCs"
  value = {
    for k, v in aws_vpc.main : k => v.id
  }
}

output "vpc_cidr_blocks" {
  description = "CIDR blocks of the created VPCs"
  value = {
    for k, v in aws_vpc.main : k => v.cidr_block
  }
}

# Subnet Information
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value = {
    for k, v in aws_subnet.public : split("-", k)[0] => v.id...
  }
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value = {
    for k, v in aws_subnet.private : split("-", k)[0] => v.id...
  }
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value = {
    for k, v in aws_subnet.database : split("-", k)[0] => v.id...
  }
}

# Load Balancer Information
output "production_alb_dns_name" {
  description = "DNS name of the production ALB"
  value       = aws_lb.production.dns_name
}

output "development_alb_dns_name" {
  description = "DNS name of the development ALB"
  value       = aws_lb.development.dns_name
}

# Database Information
output "production_db_endpoint" {
  description = "Endpoint of the production RDS instance"
  value       = aws_db_instance.production.endpoint
}

output "development_db_endpoint" {
  description = "Endpoint of the development RDS instance"
  value       = aws_db_instance.development.endpoint
}

output "shared_db_endpoint" {
  description = "Endpoint of the shared services RDS instance"
  value       = aws_db_instance.shared_services.endpoint
}

# Bastion Host Information
output "bastion_public_ip" {
  description = "Public IP of the bastion host"
  value       = aws_instance.bastion.public_ip
}

output "bastion_private_ip" {
  description = "Private IP of the bastion host"
  value       = aws_instance.bastion.private_ip
}

# Auto Scaling Group Information
output "production_asg_name" {
  description = "Name of the production Auto Scaling Group"
  value       = aws_autoscaling_group.production.name
}

output "development_asg_name" {
  description = "Name of the development Auto Scaling Group"
  value       = aws_autoscaling_group.development.name
}

# Security Group Information
output "security_group_ids" {
  description = "IDs of the created security groups"
  value = {
    production_web     = aws_security_group.production_web.id
    production_alb     = aws_security_group.production_alb.id
    production_db      = aws_security_group.production_db.id
    development_web    = aws_security_group.development_web.id
    development_alb    = aws_security_group.development_alb.id
    development_db     = aws_security_group.development_db.id
    shared_db          = aws_security_group.shared_db.id
    bastion            = aws_security_group.bastion.id
  }
}

# VPC Peering Information
output "vpc_peering_connections" {
  description = "IDs of the VPC peering connections"
  value = {
    prod_to_dev     = aws_vpc_peering_connection.prod_to_dev.id
    prod_to_shared  = aws_vpc_peering_connection.prod_to_shared.id
    dev_to_shared   = aws_vpc_peering_connection.dev_to_shared.id
    prod_to_dmz     = aws_vpc_peering_connection.prod_to_dmz.id
    dev_to_dmz      = aws_vpc_peering_connection.dev_to_dmz.id
  }
}

# CloudWatch Log Groups
output "cloudwatch_log_groups" {
  description = "Names of the CloudWatch log groups"
  value = {
    for k, v in aws_cloudwatch_log_group.vpc_flow_logs : k => v.name
  }
}

# Connection Information
output "connection_info" {
  description = "Connection information for the multi-VPC environment"
  value = {
    production_alb_url = "http://${aws_lb.production.dns_name}"
    development_alb_url = "http://${aws_lb.development.dns_name}"
    bastion_host = "ssh -i ssh_key ec2-user@${aws_instance.bastion.public_ip}"
    bastion_web = "http://${aws_instance.bastion.public_ip}"
  }
}

# Architecture Summary
output "architecture_summary" {
  description = "Summary of the multi-VPC architecture"
  value = {
    vpcs = {
      production = {
        cidr = aws_vpc.main["production"].cidr_block
        public_subnets = length([for s in aws_subnet.public : s if split("-", s.tags["Name"])[1] == "production"])
        private_subnets = length([for s in aws_subnet.private : s if split("-", s.tags["Name"])[1] == "production"])
        database_subnets = length([for s in aws_subnet.database : s if split("-", s.tags["Name"])[1] == "production"])
      }
      development = {
        cidr = aws_vpc.main["development"].cidr_block
        public_subnets = length([for s in aws_subnet.public : s if split("-", s.tags["Name"])[1] == "development"])
        private_subnets = length([for s in aws_subnet.private : s if split("-", s.tags["Name"])[1] == "development"])
        database_subnets = length([for s in aws_subnet.database : s if split("-", s.tags["Name"])[1] == "development"])
      }
      dmz = {
        cidr = aws_vpc.main["dmz"].cidr_block
        public_subnets = length([for s in aws_subnet.public : s if split("-", s.tags["Name"])[1] == "dmz"])
        private_subnets = length([for s in aws_subnet.private : s if split("-", s.tags["Name"])[1] == "dmz"])
      }
      shared_services = {
        cidr = aws_vpc.main["shared_services"].cidr_block
        public_subnets = length([for s in aws_subnet.public : s if split("-", s.tags["Name"])[1] == "shared_services"])
        private_subnets = length([for s in aws_subnet.private : s if split("-", s.tags["Name"])[1] == "shared_services"])
        database_subnets = length([for s in aws_subnet.database : s if split("-", s.tags["Name"])[1] == "shared_services"])
      }
    }
    resources = {
      load_balancers = 2
      auto_scaling_groups = 2
      rds_instances = 3
      security_groups = 8
      vpc_peering_connections = 5
      cloudwatch_alarms = 8
    }
  }
}
