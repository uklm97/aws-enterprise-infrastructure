# Multi-VPC AWS Environment Architecture

## Overview

This Terraform configuration creates a comprehensive multi-VPC AWS environment designed for production workloads with proper separation of concerns, security, and scalability.

## Architecture Components

### 1. VPCs (Virtual Private Clouds)

The environment consists of four distinct VPCs:

#### Production VPC (10.0.0.0/16)
- **Purpose**: High-availability production workloads
- **Components**: 
  - Auto Scaling Group with 2-4 instances
  - Application Load Balancer
  - RDS MySQL database (Multi-AZ)
  - Private subnets for application servers
  - Database subnets for RDS instances

#### Development VPC (10.1.0.0/16)
- **Purpose**: Development and testing environment
- **Components**:
  - Auto Scaling Group with 1-2 instances
  - Application Load Balancer
  - RDS MySQL database (Single-AZ for cost optimization)
  - Private subnets for development servers

#### DMZ VPC (10.2.0.0/16)
- **Purpose**: Public-facing services and secure access
- **Components**:
  - Bastion host for SSH access
  - Public subnets for internet-facing services
  - Security-focused configuration

#### Shared Services VPC (10.3.0.0/16)
- **Purpose**: Common services and databases
- **Components**:
  - RDS MySQL database (Multi-AZ)
  - Monitoring and logging services
  - Shared resources accessible by other VPCs

### 2. Networking

#### Subnet Architecture
Each VPC follows a three-tier subnet design:

1. **Public Subnets** (10.x.1.0/24, 10.x.2.0/24, 10.x.3.0/24)
   - Internet-facing resources
   - Load balancers
   - Bastion hosts
   - NAT Gateways

2. **Private Subnets** (10.x.11.0/24, 10.x.12.0/24, 10.x.13.0/24)
   - Application servers
   - Internal services
   - No direct internet access

3. **Database Subnets** (10.x.21.0/24, 10.x.22.0/24, 10.x.23.0/24)
   - RDS instances
   - Database servers
   - Highest security isolation

#### VPC Peering
All VPCs are interconnected via VPC peering connections:
- Production ↔ Development
- Production ↔ Shared Services
- Development ↔ Shared Services
- Production ↔ DMZ
- Development ↔ DMZ

#### Route Tables
- **Public Route Tables**: Route to Internet Gateway
- **Private Route Tables**: Route to NAT Gateway + VPC peering routes
- **Database Route Tables**: Same as private, additional security

### 3. Security

#### Security Groups
Each environment has specific security groups:

**Production:**
- `production-web-sg`: Web servers (HTTP/HTTPS from ALB, SSH from bastion)
- `production-alb-sg`: Load balancer (HTTP/HTTPS from internet)
- `production-db-sg`: Database (MySQL from web servers)

**Development:**
- `development-web-sg`: Web servers (HTTP/HTTPS from ALB, SSH from bastion)
- `development-alb-sg`: Load balancer (HTTP/HTTPS from internet)
- `development-db-sg`: Database (MySQL from web servers)

**Shared Services:**
- `shared-db-sg`: Database (MySQL from production and development)

**DMZ:**
- `bastion-sg`: Bastion host (SSH from internet)

#### Network ACLs
- Stateless packet filtering at subnet level
- Allow HTTP (80), HTTPS (443), SSH (22)
- Allow ephemeral ports (1024-65535)
- Applied to all subnets in each VPC

### 4. Compute Resources

#### Auto Scaling Groups
- **Production**: 2-4 instances across 3 AZs
- **Development**: 1-2 instances across 3 AZs
- Health checks and automatic scaling policies
- CPU-based scaling triggers

#### Launch Templates
- Amazon Linux 2 AMI
- User data script for application deployment
- Security group assignments
- Key pair configuration

#### Bastion Host
- Single instance in DMZ VPC
- SSH access to private instances
- Enhanced security configuration
- Monitoring and logging

### 5. Load Balancing

#### Application Load Balancers
- **Production ALB**: High-availability load distribution
- **Development ALB**: Development environment load distribution
- Health checks and target group configuration
- HTTP listener on port 80

#### Target Groups
- Health check configuration
- Instance registration
- Load balancing algorithm (round-robin)

### 6. Database Layer

#### RDS Instances
- **Production**: Multi-AZ MySQL 8.0
- **Development**: Single-AZ MySQL 8.0 (cost optimization)
- **Shared Services**: Multi-AZ MySQL 8.0
- Encrypted storage
- Automated backups
- Parameter and option groups

### 7. Monitoring and Logging

#### CloudWatch
- VPC Flow Logs for network monitoring
- Custom metrics for EC2 and RDS
- CloudWatch alarms for auto scaling
- Log aggregation and analysis

#### CloudWatch Alarms
- CPU utilization thresholds
- Database connection monitoring
- Auto scaling triggers
- Multi-dimensional monitoring

## Security Best Practices

### Network Security
1. **Least Privilege**: Security groups allow only necessary traffic
2. **Network Isolation**: Private subnets for sensitive resources
3. **VPC Peering**: Controlled inter-VPC communication
4. **Flow Logs**: Network traffic monitoring and analysis

### Access Control
1. **SSH Key Authentication**: No password authentication
2. **Bastion Host**: Single point of SSH access
3. **Security Groups**: Stateful firewall rules
4. **Network ACLs**: Stateless packet filtering

### Data Protection
1. **Encryption at Rest**: RDS storage encryption
2. **Encryption in Transit**: HTTPS and SSH
3. **Backup Strategy**: Automated RDS backups
4. **Multi-AZ Deployment**: High availability for production

## Scalability Features

### Auto Scaling
- CPU-based scaling policies
- Health check integration
- Multi-AZ deployment
- Configurable scaling thresholds

### Load Balancing
- Application Load Balancer
- Health check monitoring
- Automatic failover
- SSL termination support

### Database Scaling
- Read replicas capability
- Multi-AZ deployment
- Automated backups
- Storage auto-scaling

## Cost Optimization

### Development Environment
- Single-AZ RDS deployment
- Smaller instance types
- Reduced backup retention
- Minimal auto scaling

### Production Environment
- Multi-AZ for high availability
- Appropriate instance sizing
- Comprehensive monitoring
- Full backup strategy

## Deployment Instructions

### Prerequisites
1. AWS CLI configured
2. Terraform >= 1.0
3. Appropriate AWS permissions
4. SSH key pair

### Steps
1. Copy `terraform.tfvars.example` to `terraform.tfvars`
2. Customize variables as needed
3. Run `terraform init`
4. Run `terraform plan`
5. Run `terraform apply`

### Post-Deployment
1. Access applications via ALB URLs
2. SSH to bastion host for server access
3. Monitor CloudWatch metrics
4. Configure additional security as needed

## Maintenance and Operations

### Regular Tasks
- Monitor CloudWatch alarms
- Review VPC Flow Logs
- Update security groups as needed
- Scale resources based on demand

### Backup and Recovery
- RDS automated backups
- Manual snapshots for critical data
- Cross-region backup replication
- Disaster recovery planning

### Security Updates
- Regular security group reviews
- Network ACL updates
- Bastion host maintenance
- Key rotation procedures

## Troubleshooting

### Common Issues
1. **VPC Peering**: Check route table configurations
2. **Security Groups**: Verify ingress/egress rules
3. **Load Balancer**: Check target group health
4. **Auto Scaling**: Review CloudWatch alarms

### Monitoring Tools
- CloudWatch Metrics
- VPC Flow Logs
- RDS Performance Insights
- Application Load Balancer access logs

## Future Enhancements

### Potential Improvements
1. **Transit Gateway**: For larger scale deployments
2. **WAF**: Web Application Firewall
3. **CloudFront**: Content delivery network
4. **ElastiCache**: Redis/Memcached caching
5. **S3**: Object storage integration
6. **Lambda**: Serverless functions
7. **API Gateway**: REST API management
8. **Route 53**: DNS management and health checks
