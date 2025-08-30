# Multi-VPC AWS Environment

This project creates a comprehensive multi-VPC AWS environment using Terraform with the following components:

## Architecture Overview

- **Production VPC**: High-availability production environment
- **Development VPC**: Development and testing environment  
- **DMZ VPC**: Public-facing services and load balancers
- **Shared Services VPC**: Common services like databases and monitoring

## Features

- Multi-AZ deployment across 3 availability zones
- VPC peering connections between environments
- Transit Gateway for centralized routing
- Security groups and NACLs for network security
- Auto Scaling Groups for high availability
- Load Balancers for traffic distribution
- RDS databases with multi-AZ deployment
- CloudWatch monitoring and logging

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- AWS Provider >= 4.0

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the plan:
   ```bash
   terraform plan
   ```

3. Apply the infrastructure:
   ```bash
   terraform apply
   ```

4. To destroy the infrastructure:
   ```bash
   terraform destroy
   ```

## Cost Considerations

This setup creates multiple VPCs with various AWS resources. Monitor your AWS costs and consider using AWS Cost Explorer to track expenses.

## Security Notes

- All security groups are configured with least-privilege access
- Database instances are in private subnets
- Public subnets only contain load balancers and bastion hosts
- VPC Flow Logs are enabled for network monitoring
